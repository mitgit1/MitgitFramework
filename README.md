# MitgitFramework

> **Status: In Development (Alpha)**
> This framework is currently under active development. The API is subject to change. It is not recommended for production use until a stable `v1.0.0` release.

MitgitFramework is a lightweight, opinionated UI wrapper for PyQt5 designed to implement Material Design 3 (M3) principles. It abstracts the complexities of QSS (Qt Style Sheets) and custom event handling, providing a declarative API for building modern, responsive desktop applications.

The framework handles theme parsing via XML, dynamic widget rendering (including custom ripple animations), and provides a configuration-driven entry point using YAML.

## Navigation 

[Header | ](#MitgitFramework)
[Architecture Overview | ](#architecture-overview)
[Prerequisites | ](#prerequisites)
[Installation | ](#installation)

[Quick Start](#quick-start)
  - [1. Configuration](#1-configuration-mitgitfwconfigyml)
  - [2. Entry Point](#2-entry-point-mainpy)
  - [3. Application Logic](#3-application-logic-app_mainpy)

[ Configuration Schema | ](#configuration-schema-mitgitfwconfigyml)
[ API Documentation | ](#api-documentation)
[History | ](#History)

## Architecture Overview

The framework is decoupled from the business logic of the application. It consists of the following core modules:

- `runner.py`: Bootstraps the `QApplication`, parses `mitgitfwconfig.yml`, initializes the theme engine, and executes the entrypoint function.
- `theme.py`: Parses XML theme files, maintains the global color and radius state, and generates the global QSS.
- `widgets.py`: Contains low-level custom-drawn primitives (e.g., `RippleButton`, `MaterialComboBox`).
- `components.py`: High-level, composite widgets (e.g., `Frame`, `Checkbox`, `MaterialDialog`) that utilize the low-level primitives.
- `window.py`: Provides `FramelessWindow` and `TitleBar` for custom window decoration.

---

## Prerequisites

- Python 3.9+
- PyQt5
- qtawesome (for SVG icon rendering)
- PyYAML (for configuration parsing)

## Installation

```bash
pip install PyQt5 qtawesome PyYAML
```

Clone the repository and place the `MitgitFramework` directory in your project root. Alternatively, install it locally:

```bash
pip install -e .
```

---

## Quick Start

### 1. Configuration (`mitgitfwconfig.yml`)

Create a YAML file in the root of your project:

```yaml
entrypoint: "app_main:setup"
window:
  title: "Mitgit App"
  width: 1024
  height: 768
  custom_frame: false
  icon: "assets/icon.ico"
theme: "md3"
qt_style: "Fusion"
```

### 2. Entry Point (`main.py`)

```python
from MitgitFramework import run

if __name__ == "__main__":
    run()
```

### 3. Application Logic (`app_main.py`)

```python
from MitgitFramework import Frame, Button, MaterialDialog

def setup(window):
    # Initialize root container
    root = Frame(variant="surface_container", padding=24, layout="vbox")
    
    # Create and bind an event to a button
    btn = Button("Initialize", variant="primary")
    btn.clicked.connect(lambda: MaterialDialog(window, "System", "Initialization complete.").exec_())
    
    root.add(btn)
    window.setCentralWidget(root)
```

---

## Configuration Schema (`mitgitfwconfig.yml`)

| Key | Type | Description |
| :--- | :--- | :--- |
| `entrypoint` | `str` | Required. Format: `"module_name:function_name"`. The function must accept a `QMainWindow` instance. |
| `window.title` | `str` | Application title. |
| `window.width` | `int` | Default window width in pixels. |
| `window.height` | `int` | Default window height in pixels. |
| `window.custom_frame` | `bool` | If `true`, uses `FramelessWindow` with a custom title bar. If `false`, uses standard OS decoration. |
| `window.icon` | `str` | Relative path to the window icon. |
| `theme` | `str` | Name of the built-in theme (e.g., `"md3"`) or a relative path to a custom `.xml` file. |
| `qt_style` | `str` | Qt application style. `"Fusion"` is strictly recommended for consistent QSS behavior. |

---

## API Documentation

All components are imported directly from `MitgitFramework`.

### Layout Containers

#### `Frame`
A stylized container widget with optional background, rounded corners, and border.

```python
Frame(
    parent=None,
    variant="surface_container",
    padding=15,
    layout="vbox",
    spacing=8,
    border=False
)
```

- `variant` (str): Background color token from the theme (e.g., `surface_container`, `surface_container_low`, `transparent`).
- `layout` (str): `"vbox"` for `QVBoxLayout` or `"hbox"` for `QHBoxLayout`.
- `border` (bool): If `True`, draws a 1px border using the `outline_variant` color.

**Methods:**
- `add(widget, stretch=0)`: Appends a widget to the frame's layout.
- `add_layout(layout)`: Appends a nested layout.

### Input Components

#### `Button`
A button widget with a built-in material ripple effect on mouse press.

```python
Button(
    text="",
    variant="primary",
    parent=None,
    icon=None,
    border_radius=None
)
```

- `variant` (str):
  - `"primary"`: Theme primary color.
  - `"play"`: Custom green (usually for launch actions).
  - `"surface"`: Elevated surface color.
  - `"danger"`: Theme error color.
  - `"text"`: Transparent background, colored text.
- `icon` (`QIcon`): Optional icon to prepend.

#### `Input`
A standard text input styled for M3.

```python
Input(placeholder="Enter text...")
```

#### `ComboBox`
A dropdown menu that overrides the native OS rendering to match the theme. Features custom item delegation and rounded popup.

```python
ComboBox()
```

#### `Checkbox`
An animated checkbox that animates the fill state on toggle. Supports mutually exclusive grouping.

```python
Checkbox(text="Option", group_id=None)
```

- `group_id` (str): If multiple checkboxes share the same `group_id`, checking one will automatically uncheck the others (mimicking radio button behavior while retaining checkbox visuals).

### Navigation

#### `NavButton`
A specialized button designed for side navigation rails.

```python
NavButton(text="Home", icon=None)
```

Renders an icon centered in a capsule (when active) with text positioned below. Requires `setCheckable(True)`.

### Dialogs

#### `MaterialDialog`
An in-app modal overlay. Instead of spawning a new OS window, it renders a semi-transparent scrim over the parent window and displays a centered card.

```python
MaterialDialog(
    parent,
    title,
    text,
    is_confirm=False
)
```

- Returns a `QDialog` instance. Use `.exec_()` to block execution.
- `is_confirm` (bool): If `True`, renders "Yes" and "No" buttons. If `False`, renders a single "OK" button.

---

## Theming System

Themes are defined via XML files. The framework ships with `md3.xml` (Material Design 3 Dark).

### XML Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<theme name="Material Design 3">
    <colors>
        <color name="primary">#D0BCFF</color>
        <color name="surface">#141218</color>
        <!-- Define all required color tokens here -->
    </colors>
    <radius>
        <value name="small">8</value>
        <value name="medium">12</value>
        <value name="large">16</value>
    </radius>
    <template><![CDATA[
        QWidget {
            background-color: {surface};
            color: {on_surface};
        }
        QPushButton {
            border-radius: {radius_small}px;
        }
    ]]></template>
</theme>
```

### Placeholder Resolution

During boot, the framework iterates through the `<colors>` and `<radius>` nodes. It then parses the `<template>` block and replaces all occurrences of `{token_name}` with the corresponding value.

*Note: Unlike Python's `.format()` or Jinja2, the substitution engine only replaces exact bracket matches (e.g., `{surface}`). It does not interfere with CSS block syntax (e.g., `QWidget { ... }`).*

### Loading a Custom Theme

Specify the path in the configuration file:

```yaml
theme: "path/to/custom_theme.xml"
```

Or load it manually in code:

```python
from MitgitFramework import load_theme, get_global_stylesheet

load_theme("path/to/custom_theme.xml")
app.setStyleSheet(get_global_stylesheet())
```

---

## License & Disclaimer

This project is licensed under the GPLv3 License.

**PyQt5 Licensing Notice:** PyQt5 is dual-licensed under the GPLv3 and a commercial license from Riverbank Computing. By using this framework (which relies on PyQt5), your application must also comply with the GPLv3 (meaning your application must be open-source) unless you purchase a commercial PyQt5 license. If you require closed-source distribution, consider porting this framework to PySide6 (LGPL).

## History:

- 1. Just For Fun
     One evening, I was sitting at my PC and, to put it mildly, had nothing to do. I was scrolling through old chats and remembered the Minecraft [launcher](https://github.com/looztm/INLauncher). He had abandoned the project about eight months ago because it was written in Flet, which was in beta and was on its way to release; my friend was afraid that a lot would change in the API and decided to shelve the project until better times. I decided to take it on.