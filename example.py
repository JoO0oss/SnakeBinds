from snakebinds import bind, unbind
import time
import pyautogui

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
    pyautogui.click()
    time.sleep(0.05)

@bind
def click_hotkey():
    """ctrl+m_forwards"""
    for _ in range(10):
        click_delay()

@bind
def leave_hotkey():
    """ctrl+esc+!shift"""
    print("Stopping Macros.")
    unbind()

bind()
