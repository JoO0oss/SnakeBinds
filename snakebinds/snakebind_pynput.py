"""Converts snakebinds names/aliases into pynput's naming system. You can just use pynput names
entirely."""
from typing import Union

_lookup_dict = {
    "control": "ctrl",
    "control_r": "ctrl_r",
    "del": "delete",
    "back": "backspace",
    "caps": "caps_lock",
    "caps_lk": "caps_lock",
    "num_lk": "num_lock",
    "scr_lk": "scroll_lock",
    "escape": "esc",
    "ins": "insert",
    "windows": "cmd",
    "windows_r": "cmd_r",
    "super": "cmd",
    "super_r": "cmd_r",
    "media_pause": "media_play_pause",
    "media_play": "media_play_pause",
    "volume_down": "media_volume_down",
    "vol_down": "media_volume_down",
    "volume_mute": "media_volume_mute",
    "vol_mute": "media_volume_mute",
    "volume_up": "media_volume_up",
    "vol_up": "media_volume_up",
    "pg_down": "page_down",
    "pg_up": "page_up",

    "u": "up",
    "d": "down",
    "l": "left",
    "r": "right",

    "^": "up",
    "v": "down",
    "<": "left",
    ">": "right",

    "m_left": "mouse_left",
    "mleft": "mouse_left",
    "m_middle": "mouse_middle",
    "mmiddle": "mouse_middle",
    "m_right": "mouse_right",
    "mright": "mouse_right",
    "m_forwards": "mouse_button9",
    "mforwards": "mouse_button9",
    "m_button9": "mouse_button9",
    "mbutton9": "mouse_button9",
    "m_backwards": "mouse_button8",
    "mbackwards": "mouse_button8",
    "m_button8": "mouse_button8",
    "mbutton8": "mouse_button8"
}

pynput_labels = [
    "alt",
    "alt_gr",
    "alt_r",
    "backspace",
    "caps_lock",
    "cmd",
    "cmd_r",
    "ctrl",
    "ctrl_r",
    "delete",
    "down",
    "end",
    "enter",
    "esc",
    "f1",
    "f10",
    "f11",
    "f12",
    "f13",
    "f14",
    "f15",
    "f16",
    "f17",
    "f18",
    "f19",
    "f2",
    "f20",
    "f3",
    "f4",
    "f5",
    "f6",
    "f7",
    "f8",
    "f9",
    "home",
    "insert",
    "left",
    "media_next",
    "media_play_pause",
    "media_previous",
    "media_volume_down",
    "media_volume_mute",
    "media_volume_up",
    "menu",
    "num_lock",
    "page_down",
    "page_up",
    "pause",
    "print_screen",
    "right",
    "scroll_lock",
    "shift",
    "shift_r",
    "space",
    "tab",
    "up"
]


def is_valid_lookup(macro_key: str) -> bool:
    """Tells whether the given key is a valid pynput value.

    Args:
        macro_key: The key you are trying to test validity.

    Returns:
        True if it's valid, False if invalid.
    """

    # I have yet to sort out how to allow + or ! as usable macro keys.
    # I would probably say \! and \+ would work fine for future versions to implement.
    if macro_key[0] == "!":
        macro_key = macro_key[1:]

    if macro_key in _lookup_dict.keys() or macro_key in pynput_labels:
        return True

    elif len(macro_key) == 1:
        return True

    else:
        return False
    # This assumes all single characters are valid, which isn't perfect, but a programmer is much less likely to typo
    # "a" than "ctrl", for example.


def lookup_bind(bind_name: str) -> Union[str, None]:
    """Change possible aliases into pynput friendly names.
    
    Args:
        bind_name: A human readable alias.

    Returns:
        A string that pynput recognises as a key.

    """

    if not is_valid_lookup(bind_name):
        return None

    if bind_name == "play":
        print("Warning: 'play', 'pause', 'next' and 'previous' are not media keys due to the existence of the \
        pause/break key (named 'pause'), so please use 'media_play', 'media_pause' etc instead.")

    if bind_name in _lookup_dict:
        return _lookup_dict[bind_name]  # I lied, until I can be bothered to look up properly, I'm going to assume if
        # it's not an alias, it's the actual name.

    else:
        return bind_name
