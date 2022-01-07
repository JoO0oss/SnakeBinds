from snakebind import bind, unbind
import time
import pyautogui


def test_hotkey():
    """ctrl+shift+t"""
    print("Test hotkey runs.")


def alternative_test_hotkey():
    """control+shift+y"""
    print("Alternative test hotkey runs as well.")


def click_hotkey():
    """ctrl+m_forwards"""
    for _ in range(10):
        pyautogui.click()
        # WHY DOES THIS NOT WORK, BEING UNABLE TO AUTOMATE SIMPLE MOUSE CLICKS RENDERS THIS WHOLE SODDING PROJECT USELESS.
        time.sleep(0.05)


def leave_hotkey():
    """ctrl+esc+!shift"""
    unbind()
    print("Stopping Macros.")


bind(test_hotkey, alternative_test_hotkey, click_hotkey, leave_hotkey)
