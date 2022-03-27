"""Random things that need to be shared amongst windows and linux instances."""
abb = abbreviator = "."

# Just grabbed these from pynput using dir().
_pynput_labels = [
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

# Similar to pynput_labels, but these are arbitrary labels for the keyboard and mouse that are not platform specific.
snakebind_keys = [
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
    "up",

    "mouse_left",
    "mouse_middle",
    "mouse_right",
    "mouse_forward",
    "mouse_backward"
]

# Alias -> snakebind keyname.
_alias_lookup_dict = {
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
    "pause_break": "pause",

    "up": "up",
    "dn": "down",
    "lf": "left",
    "lft": "left",
    "rt": "right",

    abb+"u": "up",
    abb+"d": "down",
    abb+"l": "left",
    abb+"r": "right",

    abb+"^": "up",
    abb+"v": "down",
    abb+"<": "left",
    abb+">": "right",


    "m_left": "mouse_left",
    "mleft": "mouse_left",
    "m_middle": "mouse_middle",
    "mmiddle": "mouse_middle",
    "m_right": "mouse_right",
    "mright": "mouse_right",
    "m_forwards": "mouse_forward",
    "mforwards": "mouse_forward",
    "mouse_button9": "mouse_forward",
    "m_button9": "mouse_forward",
    "mbutton9": "mouse_forward",
    "mouse_x2": "mouse_forward",
    "m_x2": "mouse_forward",
    "mx2": "mouse_forward",
    "m_backwards": "mouse_backward",
    "mbackwards": "mouse_backward",
    "mouse_button8": "mouse_backward",
    "m_button8": "mouse_backward",
    "mbutton8": "mouse_backward",
    "mouse_x1": "mouse_backward",
    "m_x1": "mouse_backward",
    "mx1": "mouse_backward"
}