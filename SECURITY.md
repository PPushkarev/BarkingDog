# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| latest (main) | ✅ |
| older tags | ❌ |

We currently support only the latest release on `main`. Please always update before reporting a vulnerability.

---

## Reporting a Vulnerability

BarkingDog is a security tool — we take vulnerability reports seriously and respond promptly.

**Please do NOT open a public GitHub Issue for security vulnerabilities.**

Instead, report privately via one of these channels:

- **GitHub Private Advisory:** [Security → Report a vulnerability](../../security/advisories/new) *(preferred)*
- **Email:** `security@[your-domain].com` *(replace with your actual address)*

### What to include

A good report helps us act fast. Please provide:

- A clear description of the vulnerability and its potential impact
- Steps to reproduce (curl commands, payload examples, config snippets)
- Affected component (`core/evaluator.py`, Docker image, CI workflow, etc.)
- Your assessment of severity (Low / Medium / High / Critical)
- Any suggested fix, if you have one

### What to expect

| Step | Timeline |
|------|----------|
| Acknowledgement | Within **48 hours** |
| Initial assessment | Within **7 days** |
| Fix or mitigation | Within **30 days** (depending on severity) |
| Public disclosure | After fix is released and deployers have had time to update |

We follow **coordinated disclosure**: we'll work with you on timing before anything is made public. If you'd like credit in the advisory, just let us know.

---

## Scope

### In scope

- Vulnerabilities in BarkingDog's own code (`core/`, `main.py`, Docker image)
- Issues that could allow an attacker to abuse the scanner to harm a target system beyond intended test scope
- Credential/token leakage through logs, reports, or environment handling
- CI/CD workflow vulnerabilities (e.g. script injection in GitHub Actions)
- Dependency vulnerabilities with a realistic attack path

### Out of scope

- Vulnerabilities in the **target bot** being tested — BarkingDog is the tool, not the target
- Vulnerabilities in third-party LLM providers (OpenAI, Anthropic, Ollama) — report those directly to them
- Issues requiring physical access to the machine running the scanner
- Social engineering attacks against the maintainer

---

## Security Design Notes

BarkingDog is designed with the following security assumptions:

- **The `AEGIS_SECRET_TOKEN`** is the only authentication mechanism between the scanner and the target webhook. Treat it like an API key — never commit it to version control.
- **The scanner sends adversarial payloads** to the target endpoint. Ensure `aegis-scan` is an isolated endpoint that does not trigger real CRM/database actions.
- **API keys** (`AI_API_KEY`, `TELEGRAM_BOT_TOKEN`) are passed via environment variables only — never hardcoded.
- **HTML reports** may contain sanitized versions of attack payloads. Do not publish reports publicly if they contain sensitive system prompt data.

---

## Disclosure History

*No vulnerabilities have been publicly disclosed yet.*

---

*This policy is inspired by [GitHub's coordinated disclosure guidelines](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/about-coordinated-disclosure-of-security-vulnerabilities).*