# Continuous integration notes

MAH DailyDesk's supported binary release target is Windows 10/11 x64.

The `Python checks` workflow runs portable database tests on Ubuntu with Python 3.11, 3.12 and 3.13, plus an isolated Qt GUI smoke test on a **Windows** GitHub-hosted runner with `QT_QPA_PLATFORM=offscreen`. This avoids unrelated Ubuntu package-mirror DNS outages during installation of Qt platform libraries.

The official Windows release pipeline also runs the full test suite and startup-smoke-tests the frozen PyInstaller executable before any release can be published. New official releases require an approved signing provider; the existing v1.0.0 release remains unsigned.

If a GUI CI job fails, inspect the specific failed step and log before treating it as an application defect.
