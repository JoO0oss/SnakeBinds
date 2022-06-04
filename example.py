from snakebinds import bind, unbind, ctl
import time
import pyautogui
# Sneaky tip, depending on your IDE, this gives you all the nice autocompletes etc. without
# affecting your code.

pyautogui = ctl.import_pyautogui()  # Replacement threadsafe pyautogui interface.
pyautogui.PAUSE = 0  # Interacting with constants works identically.


@bind
def test_hotkey():
    """ctrl+shift+t"""
    print("Test hotkey runs.")

@bind
def alternative_test_hotkey():
    """control+shift+y"""
    print("Alternative test hotkey runs as well.")

def click_delay():
    """None-macro function, can be ran by the the programmer as normal."""
    pyautogui.click(button="left")
    time.sleep(0.05)

@bind
def click_hotkey():
    """ctrl+m_forwards"""
    for _ in range(10):
        # click_delay() is a blocking function, but will only hold things up in this function.
        click_delay()

@bind
def hold_click_hotkey():
    """alt+m_forwards"""
    # ctl.is_held() can be used to run things while the user holds the macro combination down.
    while ctl.is_held("alt+m_forwards"):
        click_delay()

@bind
def hscroll_right():
    """shift+$r"""

    # Shift + right arrow key
    pyautogui.hscroll(3)  # Scrolls to the right.

@bind
def hscroll_left():
    """shift+$<"""

    # Shift + left arrow key
    pyautogui.hscroll(-3)  # Scrolls to the left.

@bind
def leave_hotkey():
    """ctrl+esc+!shift"""
    print("Finishing up.")
    unbind()  # bind() only stops blocking after this call once all macros have finished.

print("Starting Macros.")
bind()
print("Done.")