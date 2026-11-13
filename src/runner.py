import sys
import os
import importlib
import yaml
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon

from .theme import load_theme, get_global_stylesheet
from .window import FramelessWindow


def _get_app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _resolve_path(relative_path):
    candidates = [
        os.path.join(_get_app_dir(), relative_path),
        os.path.join(os.getcwd(), relative_path),
    ]
    if hasattr(sys, "_MEIPASS"):
        candidates.insert(0, os.path.join(sys._MEIPASS, relative_path))
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def _import_entrypoint(spec):
    if ":" not in spec:
        raise ValueError(f"Entrypoint must be 'module:function', got: {spec}")
    module_path, func_name = spec.split(":", 1)
    module = importlib.import_module(module_path)
    func = getattr(module, func_name, None)
    if not callable(func):
        raise AttributeError(f"'{func_name}' in '{module_path}' is not callable")
    return func


def run(config_path="mitgitfwconfig.yml"):
    resolved_config = _resolve_path(config_path)
    if not resolved_config:
        raise FileNotFoundError(f"Config not found: {config_path}")

    with open(resolved_config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    entrypoint_spec = config.get("entrypoint")
    if not entrypoint_spec:
        raise ValueError("'entrypoint' is required in config")

    window_cfg = config.get("window", {})
    use_custom_frame = window_cfg.get("custom_frame", False)

    app = QApplication(sys.argv)
    app.setStyle(config.get("qt_style", "Fusion"))

    theme_name = config.get("theme", "md3")
    load_theme(theme_name)

    title = window_cfg.get("title", "App")
    icon_path = window_cfg.get("icon")
    icon_obj = None
    if icon_path:
        full_icon_path = _resolve_path(icon_path)
        if full_icon_path:
            icon_obj = QIcon(full_icon_path)

    if use_custom_frame:
        window = FramelessWindow(title=title, icon=icon_obj)
    else:
        window = QMainWindow()
        window.setWindowTitle(title)
        if icon_obj:
            window.setWindowIcon(icon_obj)

    window.resize(window_cfg.get("width", 1100), window_cfg.get("height", 700))
    window.setStyleSheet(get_global_stylesheet())

    entry_func = _import_entrypoint(entrypoint_spec)
    entry_func(window)

    window.show()
    sys.exit(app.exec_())
