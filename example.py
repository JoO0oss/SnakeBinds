from snakebinds import bind, unbind, ctl
import time

pyautogui = ctl.import_pyautogui()
pyautogui.PAUSE = 0


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
        click_delay()

@bind
def hold_click_hotkey():
    """alt+m_forwards"""
    while ctl.is_held("alt+m_forwards"):
        click_delay()

@bind
def hscroll_right():
    """shift+$r"""
    pyautogui.hscroll(3)

@bind
def hscroll_left():
    """shift+$<"""
    pyautogui.hscroll(-3)

@bind
def leave_hotkey():
    """ctrl+esc+!shift"""
    print("Finishing up.")
    unbind()

print("Starting Macros.")
bind()