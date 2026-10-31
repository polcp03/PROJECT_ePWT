// control - the operator interface: one button to start/stop, one LED to show the state.
// For now the board's own BOOT button (GPIO 0) and blue LED (GPIO 2): no wiring needed.
// A panel switch later only changes this module.
#pragma once

enum class LedMode { Idle, Recording, Error };

void control_begin();
bool control_pressed();          // true once per press, debounced
void control_led(LedMode mode);  // call every loop; it handles the blinking
