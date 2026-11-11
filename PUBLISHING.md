# Publishing MAH DailyDesk

The official source and Windows release live at:
https://github.com/mahmiasghar63/mah-dailydesk

## Automated Windows release

The `.github/workflows/release.yml` workflow runs on a push to `main` that changes `release/VERSION` and can also be started via **Actions → Build and publish Windows release → Run workflow**.

It runs unit and GUI tests on GitHub's hosted Windows runner, generates the app icon, captures authentic GUI screenshots with disposable demo data, builds an unsigned 64-bit PyInstaller onedir bundle, smoke-tests the executable, packages the full app folder, and creates a GitHub Release with checksum and screenshots **only after its build and tests pass**.

The version in `release/VERSION`, `pyproject.toml` and `dailydesk/__init__.py` must agree. A release is created with the tag `v<version>`. A rerun uploads assets to the same release instead of creating another tag.

## Source modifications

Edit locally, run `python -m pytest -q` and test the GUI. Push changes to `main` to run the normal Python checks. For a future official release, bump the three version locations, update `release/RELEASE_NOTES.md` and `CHANGELOG.md`, and change `release/VERSION` in the same commit.

## Manual Windows build

On Windows 10 or 11 x64, launch `run_windows.bat` to set up Python dependencies, then `build_windows.bat` to create `dist/MAH-DailyDesk/`. Distribute the **complete** directory, not the EXE alone.

The release binary is unsigned. Do not claim Microsoft code signing, antivirus certification, or an installer exists. Do not publish files containing personal notes, tasks, SQLite databases or API keys.

## GitHub repository settings (optional)

Set description to "A modern, offline-first Python productivity desktop app with tasks, notes, planner, habits, expense tracking and focus tools." Suggested topics: `python`, `pyside6`, `desktop-application`, `productivity`, `task-manager`, `sqlite`, `gui`, `open-source`.