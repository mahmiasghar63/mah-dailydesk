# Contributing to MAH DailyDesk

Thank you for helping improve **MAH DailyDesk**, an offline-first Python + PySide6 productivity app. Bug reports, documentation fixes, accessibility improvements and focused feature proposals are welcome.

## Before you start

- Read the [README](README.md) for the supported Windows release, source setup and project structure.
- Check [existing issues](https://github.com/mahmiasghar63/mah-dailydesk/issues) and [pull requests](https://github.com/mahmiasghar63/mah-dailydesk/pulls) for duplicates.
- For security vulnerabilities, **do not open a public issue with exploit details**. Follow [SECURITY.md](SECURITY.md) instead.
- Open an issue for large proposed changes before investing time in a major rewrite.

## Set up a development environment

On Windows 10/11 with Python 3.11 or newer:

```bat
git clone https://github.com/mahmiasghar63/mah-dailydesk.git
cd mah-dailydesk
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\python main.py
```

The app's supported release target is **Windows 10/11 x64**. Linux and macOS may work from source if the appropriate Qt runtime libraries are available.

## Run tests

```bat
.venv\Scripts\python -m pytest -q
.venv\Scripts\python -m compileall -q dailydesk main.py
```

The tests include SQLite business logic and an offscreen Qt GUI construction/navigation smoke test. GitHub Actions separately checks the core logic using Python 3.11, 3.12 and 3.13, and the GUI on Windows. Passing tests are necessary but do not prove that every interaction works.

When changing a data operation, add regression tests to `tests/test_storage.py`. When changing the GUI, update or add appropriate tests in `tests/test_gui.py`.

## Coding guidelines

- Keep the application **offline-first**. Do not add network telemetry, analytics, accounts or cloud sync without an explicit feature proposal.
- Use parameterized SQLite queries when handling user data. Do not concatenate untrusted input into SQL.
- Keep application data in the per-user data directory. Never write example databases or user-generated records into the tracked source tree.
- Keep UI changes keyboard-accessible and consistent with the existing theme and navigation.
- Avoid unnecessary dependencies. Do not bundle compiled packages, generated build output, virtual environments or personal data in commits.
- Preserve existing public behavior unless the pull request explicitly documents a change.

## Submitting a pull request

1. Create a topic branch, such as `fix/task-filter` or `docs/quickstart`.
2. Make one focused improvement per PR and describe **why** it is needed.
3. Run the tests and verify any affected UI manually.
4. Include a concise summary, steps to reproduce any bug, what you changed and how you verified it.
5. If your change affects a public feature, update the README or other affected documentation.

For UI changes, attach screenshots containing **demonstration data only**. For bug reports, include your operating system, Python version (when running from source), expected behavior and actual behavior. Never upload a private SQLite database, token, password, signing key or personal notes.

## Releases and security

Versioned Windows releases are managed through [PUBLISHING.md](PUBLISHING.md). The published v1.0.0 portable ZIP is unsigned. Future signed-release configuration is described in [CODE_SIGNING.md](CODE_SIGNING.md); contributors do not need signing credentials for regular source or documentation PRs.

By contributing, you agree to license your submitted code under the repository's [MIT License](LICENSE). Maintainers review and merge contributions on a best-effort basis.
