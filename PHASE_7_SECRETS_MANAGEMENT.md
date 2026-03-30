# Platinum Tier - Phase 7: Security Hardening

This documentation defines the strict rules and procedures for Secrets Management in the Platinum Tier architecture.

## 1. Secrets Management Rules

**Rule 1: Git Exclusion**
No credentials, `.env` files, `.session` folders, or `token.json` files are EVER allowed in the `AI_Employee_Vault_Sync` repository. The strict `.gitignore` configured in Phase 2 handles this, but we enforce it further with pre-commit hooks.

**Rule 2: Cloud VM Secrets Storage**
All API keys and credentials required by the Cloud VM must be stored in:
`/opt/ai-employee/.env`
This file must be locked down:
```bash
chmod 600 /opt/ai-employee/.env
```

**Rule 3: Local Mac/Windows Secrets Storage**
For maximum security on the Local Agent, use your OS Keychain (e.g., macOS Keychain Access or Windows Credential Manager) and dynamically load them into the environment variables during the `local_agent.py` startup, or keep a tightly secured `.env` that is strictly outside the Vault folder.

## 2. Setting Up the Pre-Commit Hook

To ensure no one accidentally commits a `.env` file, we install a Git pre-commit hook in the repository.

Run these commands on BOTH your Local Machine and Cloud VM:

```bash
cd AI_Employee_Vault_Sync
mkdir -p .git/hooks

cat << 'EOF' > .git/hooks/pre-commit
#!/bin/sh
# Prevent committing .env files or tokens
if git diff --cached --name-only | grep -E '(\.env|token\.json|credentials\.json|\.session|\.key|\.pem)'; then
  echo "🚨 SECURITY VIOLATION: You are attempting to commit a blocked credential file."
  echo "See strict .gitignore rules. Commit aborted."
  exit 1
fi
EOF

chmod +x .git/hooks/pre-commit
```

## 3. DRY_RUN Enforcement

By default, the `local_agent.py` script starts with `DRY_RUN=true`.
Unless you explicitly export `DRY_RUN=false` in your terminal or `.env`, the Local Agent will only simulate actions without making real API calls.

To run locally in production mode:
```bash
export DRY_RUN=false
python local_agent.py
```

## 4. Auditing

The `audit_secret_access.py` script acts as a proxy wrapper around your `.env` reading process out of Python. If you want extreme paranoia, you can import its functions instead of `dotenv` directly, to log every time a script attempts to read the Facebook password or Gmail token.
