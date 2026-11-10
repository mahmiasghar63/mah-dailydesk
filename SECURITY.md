# Security and privacy

MAH DailyDesk stores information locally in SQLite, without authentication or remote sync. Anyone who can access your OS account may be able to read its local database or exported CSV files. Protect your computer account and your backups.

Do not publish files containing personal data or API keys. `.gitignore` excludes common SQLite/database files, but you should still review `git status` before every commit.

To report a vulnerability, use a private disclosure channel if the repository provides one; otherwise avoid posting sensitive exploit details or user data in public issues.