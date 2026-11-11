# Continuous integration notes

Qt GUI tests on Ubuntu require system libraries including libEGL.so.1. The GitHub Actions workflow installs `libegl1`, `libopengl0`, `libxkbcommon-x11-0`, and `libxcb-cursor0` before launching PySide6 with `QT_QPA_PLATFORM=offscreen`.
