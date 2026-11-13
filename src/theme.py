import os
import xml.etree.ElementTree as ET
COLORS = {}
RADIUS = {}
_current_template = ""
def _load_theme_from_xml(path: str):
    global _current_template
    tree = ET.parse(path)
    root = tree.getroot()
    COLORS.clear()
    for c in root.findall("./colors/color"):
        COLORS[c.attrib["name"]] = c.text.strip()
    RADIUS.clear()
    for r in root.findall("./radius/value"):
        RADIUS[r.attrib["name"]] = int(r.text.strip())
    template_el = root.find("template")
    if template_el is not None and template_el.text:
        _current_template = template_el.text
    else:
        _current_template = ""
def load_theme(theme_name_or_path: str = "md3"):
    if theme_name_or_path.endswith(".xml"):
        path = theme_name_or_path
    else:
        themes_dir = os.path.join(os.path.dirname(__file__), "themes")
        path = os.path.join(themes_dir, f"{theme_name_or_path}.xml")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл темы не найден: {path}")
    _load_theme_from_xml(path)
def get_global_stylesheet() -> str:
    """Возвращает готовый QSS с безопасной заменой плейсхолдеров."""
    data = dict(COLORS)
    for k, v in RADIUS.items():
        data[f"radius_{k}"] = str(v)
    result = _current_template
    for key, value in data.items():
        result = result.replace(f"{{{key}}}", value)
    return result
try:
    load_theme("md3")
except Exception as e:
    print(f"[MitgitFramework] Failed to load default theme: {e}")
