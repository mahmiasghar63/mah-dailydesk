# Publishing MAH DailyDesk

The official source and Windows release live at:
https://github.com/mahmiasghar63/mah-dailydesk

## Automated Windows release

The `.github/workflows/release.yml` workflow runs on a push to `main` that changes `release/VERSION` (not every source-code push) and can also be started via **Actions → Build and publish Windows release → Run workflow**.

It runs unit and GUI tests on GitHub's hosted Windows runner, generates the app icon, captures authentic GUI screenshots with disposable demo data, builds a 64-bit PyInstaller onedir bundle, smoke-tests the executable, requires verified SignPath Foundation or Azure Artifact Signing, validates its Authenticode signature and timestamp, packages the signed app folder, creates a GitHub build-provenance attestation, and publishes the GitHub Release with checksum and screenshots **only after every check succeeds**. The publisher credentials and service account must be connected before the next release can run. The existing v1.0.0 remains unsigned.

The version in `release/VERSION`, `pyproject.toml` and `dailydesk/__init__.py` must agree. A release is created with the tag `v<version>`. An existing release tag is never overwritten by automation. To ship new binaries, bump the version and create a new tag; rerunning an already-published version intentionally fails to protect release integrity.

## Source modifications

Edit locally, run `python -m pytest -q` and test the GUI. Push changes to `main` to run the normal Python checks. For a future official release, bump the three version locations, update `release/RELEASE_NOTES.md` and `CHANGELOG.md`, and change `release/VERSION` in the same commit.

## Verify the release download

In PowerShell, from the folder containing the downloaded ZIP and `SHA256SUMS.txt`:

```powershell
Get-FileHash -Algorithm SHA256 .\MAH-DailyDesk-v1.0.0-Windows-x64.zip
Get-Content .\SHA256SUMS.txt
```

Compare the two hexadecimal hashes exactly. The hash verifies download integrity against the release checksum, but does not prove the unsigned binary is malware-free. Only use files from the official repository.

## Security checks

GitHub Actions runs core and GUI tests on pushes. The `Security checks` workflow runs dependency vulnerability checks and a source scan on pushes, pull requests and weekly; Dependabot opens dependency update pull requests. Review any security findings before publishing another version.

## Manual Windows build

On Windows 10 or 11 x64, launch `run_windows.bat` to set up Python dependencies, then `build_windows.bat` to create `dist/MAH-DailyDesk/`. Distribute the **complete** directory, not the EXE alone.

The existing v1.0.0 release is unsigned. New versions will require a signing provider; the workflow refuses to publish unsigned releases. Do not claim antivirus certification or a signed installer exists. Do not publish files containing personal notes, tasks, SQLite databases or API keys.

## Code signing (integration ready; provider not connected)

The build pipeline is configured for **SignPath Foundation** (recommended for eligible open-source projects) or **Azure Artifact Signing** (where available). It enforces signing, verifies the returned executable and timestamp, and generates GitHub provenance attestations for new release ZIPs. **The project still needs an approved external signing provider**, and v1.0.0 is still unsigned. See [CODE_SIGNING.md](CODE_SIGNING.md) for exactly which GitHub secrets and variables to configure. Never commit signing credentials.

## GitHub repository settings (optional)

Set description to "A modern, offline-first Python productivity desktop app with tasks, notes, planner, habits, expense tracking and focus tools." Suggested topics: `python`, `pyside6`, `desktop-application`, `productivity`, `task-manager`, `sqlite`, `gui`, `open-source`.