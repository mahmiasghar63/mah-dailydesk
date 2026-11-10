# Publishing MAH DailyDesk on GitHub

## Repository settings

- **Owner:** `mahmiasghar63`
- **Repository:** `mah-dailydesk`
- **Description:** A modern, offline-first Python productivity desktop app with tasks, notes, planner, habits, expense tracking and focus tools.
- **Visibility:** Public
- **Branch:** `main`
- **License:** MIT (included in source)
- **Topics:** `python`, `pyside6`, `desktop-application`, `productivity`, `task-manager`, `sqlite`, `gui`, `open-source`
- **Initial README/.gitignore/license on GitHub setup:** leave disabled, because the source already provides these.

## Create the empty repository

1. Open https://github.com/new while signed in to the correct account.
2. Enter the repository details above.
3. Click **Create repository**.

## Upload all source files using Git for Windows

Open Command Prompt in the **extracted `mah-dailydesk` folder**. Use these commands:

```bat
git init -b main
git add .
git commit -m "feat: initial MAH DailyDesk source preview"
git remote add origin https://github.com/mahmiasghar63/mah-dailydesk.git
git push -u origin main
```

If Git is not found, install Git for Windows. Sign in to GitHub when your credential manager opens; your GitHub password alone is not a valid command-line Git password.

## Check the public repository

Verify that all source folders, the GitHub Actions workflow, license, README and documentation are present. Check **Actions** for Python test results. Add repository topics through the About settings on GitHub.

## Tag a release after testing

Don't claim a stable binary release until the GUI starts successfully and the features work on Windows. After testing, build with `build_windows.bat`, check the entire `dist/MAH-DailyDesk/` folder on a clean machine, and attach a zipped build folder in **Releases** with a clear version and release notes.