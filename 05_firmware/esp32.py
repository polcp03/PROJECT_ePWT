"""ESP32 workbench: compile, flash and watch the serial port without the Arduino IDE.

One long-running monitor window shows everything: compiler output, upload progress
and every Serial.print of the board. Claude runs `flash` from another terminal; the
monitor sees the request, releases the port, shows the build, and reopens the port.

    python esp32.py monitor                      # leave it open in a visible terminal
    python esp32.py compile arduino/can_logger   # compile only (no board needed)
    python esp32.py flash   arduino/can_logger   # compile + upload + monitor resumes
    python esp32.py send    start                # type a line into the board

Why the pause file: a COM port can only be open in one program at a time. If the
monitor kept it, the upload would fail with "port busy".

Everything the monitor shows also goes to .monitor/serial.log, so Claude reads the
same thing Pol sees.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE_DIR = HERE / ".monitor"
PAUSE = STATE_DIR / "pause"          # exists while a flash is in progress
TX = STATE_DIR / "tx.txt"            # lines waiting to be sent to the board
STATE = STATE_DIR / "state.json"     # last flashed sketch and its baud rate
SERIAL_LOG = STATE_DIR / "serial.log"
BUILD_LOG = STATE_DIR / "build.log"

FQBN = "esp32:esp32:esp32"
DEFAULT_PORT = "COM4"
DEFAULT_BAUD = 115200
ARDUINO_CLI = Path(os.environ.get("LOCALAPPDATA", "")) / (
    "Programs/Arduino IDE/resources/app/lib/backend/resources/arduino-cli.exe")
# USB-serial chips found on ESP32 dev boards: CP210x (Silicon Labs), CH340 (WCH), FTDI.
ESP32_USB_VIDS = {0x10C4, 0x1A86, 0x0403}

GREY, RED, GREEN, YELLOW, CYAN, RESET = (
    "\033[90m", "\033[91m", "\033[92m", "\033[93m", "\033[96m", "\033[0m")


def say(color, text):
    print(f"{color}{text}{RESET}", flush=True)


def read_state():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def sketch_baud(sketch: Path) -> int:
    """Baud rate from the first Serial.begin(N) in the sketch, so the monitor matches it."""
    for src in sorted(sketch.glob("*.ino")):
        m = re.search(r"Serial\.begin\(\s*(\d+)", src.read_text(encoding="utf-8", errors="ignore"))
        if m:
            return int(m.group(1))
    return DEFAULT_BAUD


def find_port() -> str | None:
    from serial.tools import list_ports
    ports = list(list_ports.comports())
    for p in ports:
        if p.vid in ESP32_USB_VIDS:
            return p.device
    names = [p.device for p in ports]
    return DEFAULT_PORT if DEFAULT_PORT in names else None


# ---------------------------------------------------------------- compile / flash

def run_cli(args, log):
    """Run arduino-cli, echo its output here and into build.log for the monitor."""
    cmd = [str(ARDUINO_CLI)] + args
    log.write(f"$ arduino-cli {' '.join(args)}\n")
    log.flush()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace")
    for line in proc.stdout:
        sys.stdout.write(line)
        log.write(line)
        log.flush()
    return proc.wait()


def resolve_sketch(name: str) -> Path:
    sketch = Path(name)
    if not sketch.is_absolute():
        sketch = (Path.cwd() / sketch) if (Path.cwd() / sketch).exists() else HERE / sketch
    if not sketch.is_dir():
        sys.exit(f"sketch folder not found: {name}")
    return sketch.resolve()


def cmd_compile(args, upload=False):
    sketch = resolve_sketch(args.sketch)
    STATE_DIR.mkdir(exist_ok=True)
    if upload:
        PAUSE.write_text(sketch.name, encoding="utf-8")
        time.sleep(1.0)  # give the monitor time to close the port
    try:
        with open(BUILD_LOG, "w", encoding="utf-8") as log:
            rc = run_cli(["compile", "--fqbn", FQBN, str(sketch)], log)
            if rc == 0 and upload:
                port = args.port or find_port()
                if port is None:
                    log.write("ESP32 not found on any COM port. Is the USB cable plugged in?\n")
                    print("ESP32 not found on any COM port. Is the USB cable plugged in?")
                    rc = 2
                else:
                    rc = run_cli(["upload", "--fqbn", FQBN, "-p", port, str(sketch)], log)
            log.write(f"\n== {'OK' if rc == 0 else 'FAILED'} ({sketch.name}) ==\n")
        if rc == 0 and upload:
            STATE.write_text(json.dumps({"sketch": sketch.name, "baud": sketch_baud(sketch),
                                         "flashed": datetime.now().isoformat(timespec="seconds")}),
                             encoding="utf-8")
            SERIAL_LOG.write_text("", encoding="utf-8")  # the log now belongs to the new firmware
    finally:
        PAUSE.unlink(missing_ok=True)
    return rc


# ---------------------------------------------------------------- monitor

class Monitor:
    def __init__(self, port, baud):
        self.fixed_port, self.fixed_baud = port, baud
        self.log = None
        self.typed = ""

    def emit(self, line, color=None):
        if color is None:
            low = line.lower()
            color = RED if ("error" in low or "fail" in low or "panic" in low) else (
                YELLOW if "warn" in low else "")
        say(color, line) if color else print(line, flush=True)
        self.log.write(f"{datetime.now():%H:%M:%S.%f}"[:-3] + f"  {line}\n")
        self.log.flush()

    def show_build(self):
        """While a flash is running, stream build.log into this window."""
        self.emit(f"--- flashing {PAUSE.read_text(encoding='utf-8', errors='ignore')}: port released ---", CYAN)
        pos = 0
        while PAUSE.exists():
            pos = self._tail(BUILD_LOG, pos)
            time.sleep(0.2)
        self._tail(BUILD_LOG, pos)
        self.log.close()
        self.log = open(SERIAL_LOG, "a", encoding="utf-8")  # flash truncated it

    def _tail(self, path, pos):
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                f.seek(pos)
                for line in f.read().splitlines():
                    say(GREY if not line.startswith("==") else
                        (GREEN if "OK" in line else RED), line)
                return f.tell()
        except OSError:
            return pos

    def pending_tx(self):
        lines = []
        if TX.exists():
            lines = TX.read_text(encoding="utf-8").splitlines()
            TX.unlink(missing_ok=True)
        if sys.platform == "win32":
            import msvcrt
            while msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in "\r\n":
                    lines.append(self.typed)
                    self.typed = ""
                elif ch == "\b":
                    self.typed = self.typed[:-1]
                else:
                    self.typed += ch
        return lines

    def run(self):
        import serial
        STATE_DIR.mkdir(exist_ok=True)
        self.log = open(SERIAL_LOG, "a", encoding="utf-8")
        TX.unlink(missing_ok=True)  # lines queued while no monitor was running are stale
        waiting_said = False
        while True:
            if PAUSE.exists():
                self.show_build()
                waiting_said = False
                continue
            port = self.fixed_port or find_port()
            baud = self.fixed_baud or read_state().get("baud", DEFAULT_BAUD)
            if port is None:
                if not waiting_said:
                    say(GREY, "waiting for the ESP32 (plug the USB cable)...")
                    waiting_said = True
                time.sleep(0.5)
                continue
            s = serial.Serial()
            s.port, s.baudrate, s.timeout = port, baud, 0.05
            s.dtr = s.rts = False  # opening the port must not reset the board
            try:
                s.open()
            except serial.SerialException:
                say(RED, f"{port} busy (another program has it open). Retrying...")
                time.sleep(2)
                continue
            waiting_said = False
            sketch = read_state().get("sketch", "?")
            self.emit(f"--- {port} open at {baud} baud, firmware: {sketch}. "
                      f"Type a line + Enter to send it. Ctrl+C quits. ---", GREEN)
            buf = b""
            try:
                while not PAUSE.exists():
                    buf += s.read(4096)
                    *lines, buf = buf.split(b"\n")
                    for raw in lines:
                        line = raw.decode("utf-8", errors="replace").rstrip("\r")
                        if line.strip():
                            self.emit(line)
                    for out in self.pending_tx():
                        self.emit(f"> {out}", CYAN)
                        s.write((out + "\n").encode())
            except serial.SerialException:
                self.emit("--- ESP32 disconnected ---", RED)
            finally:
                s.close()


def cmd_send(args):
    STATE_DIR.mkdir(exist_ok=True)
    with open(TX, "a", encoding="utf-8") as f:
        f.write(" ".join(args.text) + "\n")


def main():
    os.system("")  # turns on ANSI colours in the Windows console
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("monitor", help="live serial monitor (leave it open)")
    m.add_argument("--port")
    m.add_argument("--baud", type=int, help="default: the baud of the last flashed sketch")
    for name in ("compile", "flash"):
        p = sub.add_parser(name)
        p.add_argument("sketch", help="sketch folder, e.g. arduino/can_logger")
        p.add_argument("--port")
    s = sub.add_parser("send", help="send a line to the board through the open monitor")
    s.add_argument("text", nargs="+")
    args = ap.parse_args()

    if args.cmd == "monitor":
        try:
            Monitor(args.port, args.baud).run()
        except KeyboardInterrupt:
            print()
    elif args.cmd == "compile":
        sys.exit(cmd_compile(args))
    elif args.cmd == "flash":
        sys.exit(cmd_compile(args, upload=True))
    else:
        cmd_send(args)


if __name__ == "__main__":
    main()
