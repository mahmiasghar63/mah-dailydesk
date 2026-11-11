# Security and privacy policy

MAH DailyDesk is an **offline-first desktop application** that stores tasks, notes, plans, habits, expenses, focus sessions and preferences in a local SQLite database. It does **not** provide account authentication, automatic cloud synchronization, or at-rest database encryption.

## Supported versions

| Version | Security support |
| --- | --- |
| 1.0.x | Best-effort security maintenance |
| 0.x and older | Unsupported |

Security updates and support are provided on a best-effort basis; there is no guaranteed response time or fixed patch schedule.

## Report vulnerabilities responsibly

**Do not publish exploit details, credentials, database contents or personally identifying information in a public GitHub issue.**

1. Open the repository's [Security tab](https://github.com/mahmiasghar63/mah-dailydesk/security).
2. If **Report a vulnerability** is available, use that private reporting channel and include a concise description, affected version, reproduction steps and likely impact.
3. If private vulnerability reporting is not available, create a public issue requesting **a private way to contact the maintainer**, without disclosing the vulnerability itself.

Please allow a reasonable opportunity for review and correction before any public disclosure. There is no formal security-response service-level agreement.

For **ordinary bugs that are not security-sensitive**, use [GitHub Issues](https://github.com/mahmiasghar63/mah-dailydesk/issues).

## Local data and privacy

- On Windows, the default SQLite file is under `%LOCALAPPDATA%\MAH-DailyDesk\dailydesk.sqlite3`.
- On Linux, it is under `~/.local/share/MAH-DailyDesk/dailydesk.sqlite3` (or `$XDG_DATA_HOME`).
- Anyone with access to the operating-system account or unprotected backup/export files may be able to read the saved data. Use a protected OS account and store backups privately.
- The application does not transmit your content to a hosted service. Manually exported CSV files and copied backups remain **your responsibility**.
- Treat CSV files from untrusted sources carefully. The app neutralizes common spreadsheet-formula prefixes in its own CSV exports, but spreadsheet applications have their own security considerations.

## Release trust and verification

The published [v1.0.0 Windows release](https://github.com/mahmiasghar63/mah-dailydesk/releases/tag/v1.0.0) is an **unsigned**, portable ZIP; it is not a signed installer or Microsoft Store app. The official release includes a `SHA256SUMS.txt` checksum. Compare the ZIP's hash using PowerShell:

```powershell
Get-FileHash -Algorithm SHA256 .\MAH-DailyDesk-v1.0.0-Windows-x64.zip
Get-Content .\SHA256SUMS.txt
```

The hashes must match exactly. A matching checksum checks against the published checksum; it does **not** establish that a binary is malware-free or identify a trusted publisher.

Future release automation is configured to **require** approved external Windows Authenticode signing and verification before publication. An external provider is not connected yet; see [CODE_SIGNING.md](CODE_SIGNING.md). No certificate, API token or signing key should ever be committed to this repository.

The repository runs automated dependency auditing and source-code security checks. These tools reduce risk, but their results are not proof that no vulnerabilities exist. The Bandit source scan currently excludes its broad `B608` SQL-string-construction heuristic; fixed SQL fragments and parameter binding should still be inspected during security reviews.

## Maintainer and contributor hygiene

- Keep secrets, API tokens, personal database files and backups out of commits, pull requests, screenshots and bug reports.
- The [`.gitignore`](.gitignore) excludes common local data files, but is not a substitute for reviewing changed files before committing.
- Run automated tests and dependency checks before proposing a security-related change.
