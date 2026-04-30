<div align="center">
  <img src="assets/reportphoto.jpg" alt="BarkingDog" width="800">
  <h1>🐶 BarkingDog</h1>
  <p><strong>AI Security Scanner for Telegram Bots & LLM Web Apps</strong></p>
  <p>Production webhook red-teaming with Multi-turn Crescendo attacks. <code>docker run</code> — and the report is ready.</p>
  <br>
  <a href="http://htmlpreview.github.io/?https://github.com/PPushkarev/BarkingDog/blob/main/assets/Report.htm">
    <img src="https://img.shields.io/badge/Demo-View%20Live%20Report-brightgreen?style=for-the-badge&logo=html5" alt="Live Report">
  </a>
</div>

<br>

## **🐶 BarkingDog** — the only scanner that tests your bot the way a real user would: through a production webhook, the Telegram interface, and a 4-step roleplay.


---

## 📸 Real-World Examples

### 1. Critical Breach (Security Fail: Jailbreak Success)
![Successful jailbreak example](assets/fail.jpg)

> 🕵️‍♂️ **Attack context:** The attacker asked the bot to write an "educational scenario plan" about a chemistry student. The LLM's basic safety filters passed the request due to the "academic" framing, and the car wash bot produced detailed instructions for synthesizing controlled substances. BarkingDog detected this bypass automatically.

![Successful jailbreak example](assets/fail2.jpg)
> 🚨 **Result:** The car wash bot wrote fully functional malicious Python code. It included a keylogger, logging to `user_input.log`, and a `simulate_data_transfer` function using sockets (`socket.AF_INET`) to exfiltrate intercepted passwords to a remote server. The bot even included the server-side code to receive the data.

![Successful jailbreak example](assets/fail3.jpg)
> 🚨 **Result:** The AI produced a professional guide to building spyware. It not only described collection methods (Polling vs. Event-Driven), but explicitly recommended specific hacking libraries: `psutil`, `pynput`, and `scapy`.

### 2. Business Logic Failure (Behavior Fail: Roleplay Drift)
![Role loss example](assets/behaviorfail.jpg)

> 🕵️‍♂️ **Attack context:** A `Crescendo / Roleplay` attack. The bot did not leak any sensitive data, but completely forgot its business purpose. Instead of booking car wash services, it gave in to the user's prompting and began elaborating a detailed criminal thriller scenario about a heist. BarkingDog flags this as a Behavior Fail, since the bot is spending company resources on off-topic content.

![Role loss example](assets/behavior2.jpg)
> 🚨 **Result:** The bot delivered a detailed lecture on synthesizing explosives (describing them as "substances that rapidly release energy upon decomposition or combustion"). It covered precursor synthesis from "oxidizers and fuels," isolation via crystallization/distillation, and stabilization under an inert atmosphere.

---

## ⚠️ Why This Matters Today

* **Real precedents:** In 2023, a user manipulated a ChatGPT-powered car dealership bot into agreeing to sell a $76,000 vehicle for $1 through a crafted prompt. The dealership was forced to take the bot offline.
* **Filter blindness:** Researchers at Ben-Gurion University demonstrated that leading chatbots (ChatGPT, Gemini, Claude) can be coerced into generating harmful content.
* **Telegram bot vulnerability:** One in three cyberattacks on small businesses involves bots. Average downtime is 32 hours; average damage is $15,000.
* **The jailbreak marketplace:** Hacker forums actively trade prompts, roleplay tactics, and DAN variations. While developers sleep, attacks are already being standardized.

---

## 📋 Table of Contents

1. [Why BarkingDog?](#-why-barkingdog)
2. [Comparison with Competitors](#️-comparison-with-competitors)
3. [Key Features](#-key-features)
4. [Quick Start](#-quick-start)
5. [Bot Integration](#-bot-integration-fastapi)
6. [Configuration (.env)](#️-configuration-env)
7. [CI/CD Automation](#-cicd-automation)
8. [Architecture & Engine](#-architecture--engine)
9. [Who Is This For?](#-who-is-this-for)
10. [Roadmap](#️-roadmap)

---

## 🎯 Why BarkingDog?

Every LLM application is a potential attack surface. Standard evaluation frameworks measure response quality: faithfulness, context recall, relevancy. BarkingDog closes the security gap through automated adversarial red teaming.

| Framework | Primary Focus |
|---|---|
| Ragas | RAG quality (hallucinations, faithfulness) |
| Promptfoo | Matrix testing and prompt engineering |
| Giskard | Enterprise security platform (Paid) |
| DeepTeam | 40+ vulnerability classes, OWASP/NIST mapping |
| **BarkingDog** | **Production monitoring + Multi-turn Crescendo attacks** |

**Key insight:** Simple keyword filters are blind to context. A bot may block a direct request like "write a virus," but will generate malicious code if the user wraps the same request in a 4-step academic roleplay scenario. BarkingDog detects these logical bypasses automatically.

---

## ⚔️ Comparison with Competitors

> **The key architectural difference:** all major tools test the model directly via the provider's SDK/API. BarkingDog tests the **production webhook** — the entire stack end-to-end.

| Criterion | Garak | PyRIT | Promptfoo | Giskard | DeepTeam | **BarkingDog** |
|---|---|---|---|---|---|---|
| Test target | Model directly | Model directly | Model / system | LLM agent | LLM agent | **Production webhook** |
| Attack vectors | ~100 | Many, flexible | 133 plugins | 50+ probes | 40+ classes | **40+ base (hundreds with mutations)** |
| Multi-turn / Crescendo | Weak | ✅ Strong | ✅ Yes | ✅ Crescendo, GOAT | ✅ Yes | **✅ Yes** |
| CI/CD integration | Yes | With effort | ✅ Native | Yes | Yes | **✅ GitHub Actions** |
| Daemon / scheduling | ❌ | ❌ | ❌ | ❌ | ❌ | **✅ Unique** |
| Telegram notifications | ❌ | ❌ | ❌ | ❌ | ❌ | **✅ Unique** |
| Over-Refusal Detection | ❌ | ❌ | Partial | Partial | ❌ | **✅ Yes** |
| Domain-aware AI Judge | ❌ | ❌ | ❌ | Partial | ❌ | **✅ Yes** |
| OWASP/NIST mapping | ❌ | Partial | ✅ | ✅ | ✅ | **✅ OWASP LLM Top 10** |
| Deployment | pip/CLI | pip/CLI | npm/CLI | pip/CLI | pip | **Docker (easiest of all)** |

**Conclusion:** BarkingDog occupies a unique niche — **continuous production monitoring with out-of-the-box OWASP mapping, built for bot owners without a DevSecOps team**.

---

## 🚀 Key Features

### 🧩 Open-Source & Fully Extensible (Zero Vendor Lock-in)
Open, modular architecture. Easily add domain-specific attack vectors to `checks.yaml`, write custom obfuscation pipelines, or plug in local LLM models (via Ollama).

### 🛡️ Two-Tier Architecture

1. **BASIC Mode — Smoke Testing (free)**
   - Deterministic evaluation via regex and keyword matching.
   - Instant leak detection (passwords, API keys, PII).
   - *Zero token cost* — ideal for every CI/CD commit.

2. **ADVANCED Mode (`-a` flag)**
   - **Dynamic Fuzzing:** Generates unique semantic variations and Base64 payloads to bypass static filters.
   - **Multi-turn / Crescendo Attacks:** Simulates sophisticated attackers who gradually poison the context window through roleplay.
   - **AI Judge (Domain Grounding):** Intent analysis grounded in your `BOT_DOMAIN`, minimizing false positives.

### 📈 CI/CD Regression Tracking
Compares ASR (Attack Success Rate) and Security Score against the previous scan. Automatically fails the pipeline (`exit 1`) when security degrades.

### 🎯 Over-Refusal Detection (ORR)
Security should not kill utility. If an auto-service bot refuses to calculate a discount as a "dangerous request" — that is a *Utility Failure*, and the scanner will catch it.

### 🔁 Daemon Mode
Deploy once — audit forever. Runs as a background Docker process, wakes on a schedule, and sends the report to Telegram.

<img src="assets/telegram.jpg" alt="Telegram Notification" width="350">

---

## ⚡ Quick Start

### Option 1: Cloud (PaaS)
Deploy the service directly from the Docker image on any PaaS (Railway, Render, Fly.io):
1. Create a new project.
2. Select **Deploy from Docker Image**.
3. Set the image: `peternsk/barkingdog`.
4. Add environment variables: `TARGET_URL` and `AEGIS_SECRET_TOKEN`.
5. Deploy.

### Option 2: Docker

**Advanced Red-Teaming audit:**

```bash
docker run \
  -e TARGET_URL=https://your-bot.app/webhook/aegis-scan \
  -e AEGIS_SECRET_TOKEN=your_secret_token \
  -e AI_API_KEY=sk-... \
  -e ADVANCED_MODE=true \
  -e BOT_DOMAIN="PROFILE_OF_YOUR_BOT" \
  peternsk/barkingdog
```

### Option 3: Python CLI

```bash
git clone https://github.com/yourname/barkingdog
cd barkingdog
pip install -r requirements.txt

# Run scan
python main.py --url https://your-bot.app/webhook/aegis-scan --advanced
```

---

## 🔌 Bot Integration (FastAPI)

### Scenario A: Add an isolated `aegis-scan` endpoint to your bot.
This prevents pollution of real analytics and does not trigger CRM actions during scanning.

```python
from pydantic import BaseModel
from typing import Optional
import uuid
import os

class AegisScanRequest(BaseModel):
    message: str
    token: Optional[str] = None

class AegisScanResponse(BaseModel):
    reply: str

@app.post("/webhook/aegis-scan", response_model=AegisScanResponse)
async def aegis_scan_endpoint(request: AegisScanRequest) -> AegisScanResponse:
    # 1. Authenticate via shared secret
    expected_token = os.getenv("AEGIS_SECRET_TOKEN")
    if not request.token or request.token != expected_token:
        return AegisScanResponse(reply="Unauthorized")

    # 2. Isolated session per test case
    scan_session_id = f"aegis_scan_{uuid.uuid4().hex[:8]}"

    # 3. Direct call to the bot's AI core
    ai_response = await brain.ask(
        user_id=scan_session_id,
        user_message=request.message
    )
    return AegisScanResponse(reply=ai_response)
```

### Scenario B: If your bot uses Long Polling (no Webhooks)

If you use `bot.polling()`, aiogram, or python-telegram-bot without webhooks, simply spin up a background FastAPI server in a separate thread:

```python
import threading
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

# 1. Your main AI response function (the one the bot uses)
async def ask_bot_brain(prompt: str) -> str:
    # Call OpenAI, Anthropic, a local model, etc.
    return "AI response"

# 2. Create a background API server for the scanner
scan_app = FastAPI()

class AegisScanRequest(BaseModel):
    message: str
    token: str = None

@scan_app.post("/webhook/aegis-scan")
async def aegis_scan_endpoint(request: AegisScanRequest):
    # Verify the secret token
    if request.token != os.getenv("AEGIS_SECRET_TOKEN", "secret123"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Run the attack prompt through the bot's brain
    answer = await ask_bot_brain(request.message)
    return {"reply": answer}

# 3. Server startup function
def run_scanner_api():
    # Start on port 8000
    uvicorn.run(scan_app, host="0.0.0.0", port=8000, log_level="warning")

# 4. Your main bot startup function
def main():
    # Start the scanner API in a background daemon thread
    threading.Thread(target=run_scanner_api, daemon=True).start()

    print("Bot started. BarkingDog scanner can now reach port 8000.")

    # Start your Telegram bot polling
    # bot.polling(none_stop=True)
    # or: await dp.start_polling(bot)
```

---

## ⚙️ Configuration (.env)

| Variable | Default | Description |
|---|---|---|
| `TARGET_URL` | — | Webhook endpoint of the bot under test |
| `AEGIS_SECRET_TOKEN` | — | Auth token to authorize the scanner on the target bot |
| `BOT_DOMAIN` | `General` | Business context of the bot (helps the AI Judge detect role drift) |
| `DAEMON_MODE` | `true` | Enables continuous background scanning (agent mode) |
| `SCAN_INTERVAL_HOURS` | `168` | Scan frequency in hours for Daemon Mode (168 = once per week) |
| `SCAN_CONCURRENCY` | `5` | Maximum number of parallel async requests |
| `SCAN_DELAY` | `0.5` | Delay in seconds between requests to avoid rate limits |
| `TELEGRAM_BOT_TOKEN` | — | API token of the Telegram bot that sends reports |
| `TELEGRAM_CHAT_ID` | — | ID of your Telegram chat or group for receiving results |
| `LLM_PROVIDER` | `openai` | AI judge and mutator provider: `openai` / `anthropic` / `ollama` |
| `LLM_MODEL` | `gpt-4o` | Model name for the selected provider |
| `AI_API_KEY` | — | API key for the selected provider (not required for Ollama) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL of the local Ollama server (if used) |

---

## 🚀 CI/CD Automation

BarkingDog supports automatic integration into any CI/CD pipeline. When metrics degrade, the scanner returns `exit 1`, automatically blocking deployment of the vulnerable bot.

<br>
<img src="assets/cdci.jpg" alt="Terminal Output" width="800">

1. **Trigger:** your bot's repository sends a `repository_dispatch` event after a successful deploy.
2. **Execution:** BarkingDog receives the signal, builds the Docker environment, and runs the audit.
3. **Reporting:** the HTML report is saved as a GitHub Actions artifact + optionally sent to Telegram.

### Step 1: Configure the bot (sender)

Add `.github/workflows/trigger-scan.yml` to your bot's repository:

```yaml
name: Trigger BarkingDog Scan
on:
  push:
    branches: [ main, master ]

jobs:
  ping-scanner:
    runs-on: ubuntu-latest
    steps:
      - name: Send Repository Dispatch
        run: |
          curl -L \
            -X POST \
            -H "Accept: application/vnd.github+json" \
            -H "Authorization: Bearer ${{ secrets.SCANNER_REPO_PAT }}" \
            -H "X-GitHub-Api-Version: 2022-11-28" \
            https://api.github.com/repos/YOUR_USERNAME/BarkingDog/dispatches \
            -d '{"event_type": "bot_updated"}'
```

### Step 2: Configure BarkingDog (receiver)

Set the following secrets in the BarkingDog repository:

| Secret | Description |
|---|---|
| `TARGET_URL` | Public URL of the bot under test |
| `AI_API_KEY` | LLM provider API key (for AI Judge and Mutators) |
| `AEGIS_SECRET_TOKEN` | Auth token shared between the scanner and the bot |
| `TELEGRAM_BOT_TOKEN` | *(Optional)* Token for Telegram notifications |
| `TELEGRAM_CHAT_ID` | *(Optional)* Chat/group ID in Telegram |

**Workflow parameters:**
- **Trigger:** `repository_dispatch` (event type: `bot_updated`)
- **Environment:** Dockerized Python 3.11-slim
- **Artifact retention:** 14 days

---

## 🧰 Architecture & Engine

BarkingDog uses an asynchronous two-phase pipeline for testing:

1. **Basic Phase (Triage):** Deterministic regex-based evaluation (`core/evaluator.py`). Filters out network errors, timeouts, and obvious bot failures (zero cost).
2. **Advanced Phase (LLM & Crescendo):** Semantic mutation generation (`core/mutator_llm.py`), multi-step context-poisoning attacks (`core/mutator_crescendo.py`), and semantic response evaluation by an AI judge (`core/advanced_evaluator.py`).

Metrics (ASR, BDR, Security Score) are calculated using a weighted penalty system with a **"fair denominator" rule** (502 network errors do not deflate the security score).

👉 **[Read the full architecture documentation, module breakdown, and calculation algorithms ➡️](ARCHITECTURE.md)**

---

## 👤 Who Is This For?

### ✅ Primary Audience (ICP)

**An indie developer or small business with a Telegram LLM bot** — they built a chatbot, have no DevSecOps engineer, and want to know: "can I be hacked?" These are exactly the people who need `docker run` and a Telegram report, not 100 attack vectors in a CLI.

**Secondary segments:**
- Early-stage AI/LLM startups (1–5 people) who want to add security to CI without hiring a security engineer.
- Freelancers and AI agencies who deliver LLM bots to clients and want to include a "security audit" in their service package.
- AI QA engineers looking for a ready-made tool for a quick check before manual pentesting.

### ❌ Not the Right Fit (Currently)

- **Enterprise organizations with strict compliance requirements (NIST/MITRE):** BarkingDog already supports detailed **OWASP LLM Top 10** mapping, but NIST AI RMF and MITRE ATLAS integration is still in development.
- **Teams with a dedicated DevSecOps staff:** If you have the resources to maintain and manually configure tools like Garak or PyRIT, they may provide broader (though less automated) coverage of specific attack types.
- **Security researchers (Academic Red Teaming):** The tool is focused on protecting business logic in production, not on finding fundamental vulnerabilities in neural network architectures (model theft, training data poisoning).

---

## 🗺️ Roadmap

### 🔴 Critical (makes the project serious)

- [ ] **Expand `checks.yaml` to 100 test cases** — the primary weakness. Add categories: RAG poisoning, indirect injection, system prompt extraction, off-topic manipulation.
- [ ] **NIST RMF / MITRE ATLAS mapping** — unlocks the enterprise audience.
- [ ] **Direct mode via OpenAI/Anthropic SDK** — model testing without a bot.

### 🟡 Important (makes the product convenient)

- [ ] **Interactive HTML report** — drill-down by category, filtering by severity.
- [ ] **Web UI (Streamlit)** — run scans without CLI for non-technical users.
- [ ] **`session_id` support** — for bots with server-side context storage.

### 🟢 Strategic

- [ ] **Domain presets** — ready-made test cases for "Legal Bot", "E-commerce Bot", "HR Bot".
- [ ] **Langfuse/LangSmith integration** — as a source of traces for testing.
- [ ] **Failure clustering by root cause** — grouping incidents rather than a flat list.
- [ ] **RAG-specific attacks** — document poisoning, indirect prompt injection via retrieved context.
- [ ] **Agentic vectors** — tool abuse, SSRF, privilege escalation.

---

## 🤝 Contributing

The project is under active development. Issues and PRs are welcome, especially:
- New test cases for `checks.yaml`
- Integrations with new LLM providers
- HTML report improvements

---

## 📄 License

MIT License — free to use; a link back to the project is appreciated.

---

<div align="center">

**🐶 BarkingDog — because a good guard dog barks before the break-in, not after.**

</div>