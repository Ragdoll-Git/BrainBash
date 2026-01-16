## 2024-01-16 - [File Permission Security]
**Vulnerability:** The function `setup_gemini` in `main.py` created a file `~/.brainbash_secrets` containing the API key with default permissions (usually 644, rw-r--r--), making it readable by other users on the system.
**Learning:** Default `open()` follows the system umask, which is often permissive for shared systems. Sensitive files must be created with restricted permissions from the start.
**Prevention:** Use `os.open` with `0o600` (rw-------) permissions combined with `os.fdopen` to ensure the file is private upon creation, avoiding race conditions where the file is momentarily readable before `chmod`.
