# Security and privacy

MAH DailyDesk stores information locally in SQLite, without authentication or remote sync. Anyone who can access your OS account may be able to read its local database or exported CSV files. Protect your computer account and your backups.

Do not publish files containing personal data or API keys. `.gitignore` excludes common SQLite/database files, but you should still review `git status` before every commit.

To report a vulnerability, use a private disclosure channel if the repository provides one; otherwise avoid posting sensitive exploit details or user data in public issues.

## Supported versions

| Version | Security fixes |
| --- | --- |
| 1.0.x | Best-effort support |
| Older versions | Not supported |

## Responsible disclosure

Please use **GitHub's private vulnerability reporting** feature under the repository Security tab if enabled. If it is unavailable, open a public issue requesting a private contact method **without including exploit instructions, private user data, secrets, or unpublished vulnerability details**. Maintainers will review reports on a best-effort basis. No guaranteed response time is offered.

## Release trust

Releases are currently unsigned. The official Windows ZIP is built by GitHub Actions, published with a SHA-256 checksum, and smoke-tested. Checksum comparison detects mismatched downloads relative to the published checksum but is not a malware scan or publisher identity verification. Never commit code-signing certificates or private keys.
