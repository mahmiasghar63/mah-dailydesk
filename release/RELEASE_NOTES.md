# MAH DailyDesk 1.0.0

The first Windows release of **MAH DailyDesk**, an offline-first desktop productivity suite written in Python and PySide6.

**What's included:** eight interactive sections (dashboard, tasks, notes, planner, habits, expenses, focus and settings), a quick-launch command palette, local SQLite storage, backups, CSV exports, and dark/light appearance preferences.

## Download and start on Windows 10/11 (64-bit)

1. Download `MAH-DailyDesk-v1.0.0-Windows-x64.zip` from the assets below.
2. Extract **the complete ZIP**, keeping the `MAH-DailyDesk` folder intact.
3. Open the folder and run `MAH-DailyDesk.exe`. Python is **not** required.
4. Windows SmartScreen may show an *unrecognized publisher* warning because the binary is not code-signed. Download only from this official repository; do not bypass warnings for unknown or modified files.

The ZIP includes supporting DLLs and Qt files; **do not move the EXE out of its folder**. App data is saved locally under `%LOCALAPPDATA%\MAH-DailyDesk\`. Updates should preserve this folder; back up your database before replacing the app.

### Trust and verification

- Check `SHA256SUMS.txt` for the archive's SHA-256 checksum.
- This is an unsigned community release, not a Microsoft Store application.
- The packaged executable receives a startup smoke check during the Windows GitHub Actions release build. While you have tested the source application successfully, new packages may have platform-specific issues; report them under Issues.

### Screenshots

The release includes images captured from the real application in an isolated GUI session with **disposable demonstration data**.

### Support

See `README.md` for source installation and troubleshooting. Please do not upload your private database in bug reports.