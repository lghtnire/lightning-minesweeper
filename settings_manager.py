import json
import os
from copy import deepcopy

DEFAULT_SETTINGS = {
    "auto_restart_on_fail": False,
    "auto_restart_on_win": True,
    "enable_r_restart": False,
    "skin_name": "联萌经典款",
    "images_path": "images/skins/联萌经典款",
    "training_n": 4,
    "training_s1": 2,
    "training_s2": 3,
    "training_d": 3,
    "training_p": 0.5,
    "training_three_con": False,
    "training_random_mode": False,
    "training_highlight": True,
    "cell_size": 35,
}


def get_settings_path(base_dir=None):
    if base_dir is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "minesweeper_settings.json")


def _as_bool(value, default):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        v = value.strip().lower()
        if v in {"1", "true", "yes", "on"}:
            return True
        if v in {"0", "false", "no", "off"}:
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def _as_int(value, default, min_value=None, valid_values=None):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    if min_value is not None and parsed < min_value:
        return default
    if valid_values is not None and parsed not in valid_values:
        return default
    return parsed


def _as_float(value, default, min_open=None, max_open=None):
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    if min_open is not None and parsed <= min_open:
        return default
    if max_open is not None and parsed >= max_open:
        return default
    return parsed


def sanitize_training_settings(raw):
    return {
        "n": _as_int(raw.get("n"), 4, min_value=3),
        "s1": _as_int(raw.get("s1"), 2, valid_values={1, 2, 3}),
        "s2": _as_int(raw.get("s2"), 3, valid_values={1, 2, 3}),
        "d": _as_int(raw.get("d"), 3, valid_values={2, 3}),
        "p": _as_float(raw.get("p"), 0.5, min_open=0.0, max_open=1.0),
        "three_con": _as_bool(raw.get("three_con"), False),
        "random_mode": _as_bool(raw.get("random_mode"), False),
        "highlight": _as_bool(raw.get("highlight"), True),
    }


def sanitize_settings(raw):
    data = deepcopy(DEFAULT_SETTINGS)
    if not isinstance(raw, dict):
        raw = {}

    training = sanitize_training_settings(
        {
            "n": raw.get("training_n", data["training_n"]),
            "s1": raw.get("training_s1", data["training_s1"]),
            "s2": raw.get("training_s2", data["training_s2"]),
            "d": raw.get("training_d", data["training_d"]),
            "p": raw.get("training_p", data["training_p"]),
            "three_con": raw.get("training_three_con", data["training_three_con"]),
            "random_mode": raw.get("training_random_mode", data["training_random_mode"]),
            "highlight": raw.get("training_highlight", data["training_highlight"]),
        }
    )

    data["auto_restart_on_fail"] = _as_bool(raw.get("auto_restart_on_fail"), data["auto_restart_on_fail"])
    data["auto_restart_on_win"] = _as_bool(raw.get("auto_restart_on_win"), data["auto_restart_on_win"])
    data["enable_r_restart"] = _as_bool(raw.get("enable_r_restart"), data["enable_r_restart"])
    data["skin_name"] = str(raw.get("skin_name", data["skin_name"]))
    data["images_path"] = str(raw.get("images_path", data["images_path"]))
    data["training_n"] = training["n"]
    data["training_s1"] = training["s1"]
    data["training_s2"] = training["s2"]
    data["training_d"] = training["d"]
    data["training_p"] = training["p"]
    data["training_three_con"] = training["three_con"]
    data["training_random_mode"] = training["random_mode"]
    data["training_highlight"] = training["highlight"]
    data["cell_size"] = _as_int(raw.get("cell_size", raw.get("font_size", data["cell_size"])), data["cell_size"], min_value=1)

    return data


def load_game_settings(path):
    if not os.path.exists(path):
        return deepcopy(DEFAULT_SETTINGS)

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return deepcopy(DEFAULT_SETTINGS)

    return sanitize_settings(raw)


def save_game_settings(path, settings):
    data = sanitize_settings(settings)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
