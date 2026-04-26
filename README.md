🐶 BarkingDog — AI Security Scanner for Telegram Bots & Web Apps

    Black-box DevSecOps scanner for production-ready LLM applications. Tests your full AI stack: RAG + system prompt + business logic + API guardrails, not just the foundational model.

    While tools like Ragas measure quality, BarkingDog answers a different question: Can your bot be hacked in production?

Why BarkingDog?

Every LLM-powered application is a potential attack surface. Standard evaluation frameworks (Ragas, DeepEval) measure quality — faithfulness, context recall, and answer relevancy. BarkingDog fills the security gap by performing adversarial red teaming.
Framework	Primary Focus
Ragas	RAG quality (hallucinations, faithfulness)
Promptfoo	Matrix testing & Prompt engineering
Giskard	Enterprise security platform (Paid)
BarkingDog	Security Red-Teaming & Multi-turn Crescendo Attacks

Key Insight: Simple keyword filters are blind to context. A bot might block "Write a virus" but output malicious code if the user wraps it in a 4-turn academic roleplay scenario. BarkingDog detects these logic bypasses automatically.
Core Features
🛡️ Two-Layer Architecture

1. BASIC Mode (Smoke Testing):

    Fast, deterministic evaluation using Regex and keyword density matching.

    Instant detection of explicit leaks (passwords, API keys, PII).

    Zero token cost. Ideal for every commit in your CI/CD pipeline.

2. ADVANCED Mode (-a flag):

    Dynamic Fuzzing (LLM Mutator): Generates unique semantic variations and Base64 payloads on the fly to bypass hardcoded static filters.

    Multi-turn / Crescendo Attacks: Emulates sophisticated hackers by gradually poisoning the LLM context window across multiple turns (Roleplay, Context Poisoning).

    AI Judge (Domain Grounding): Analyzes intent and context based on your specific BOT_DOMAIN. It distinguishes between a genuine jailbreak and a polite business refusal, minimizing false positives.

📈 CI/CD Regression Tracking

BarkingDog compares the current ASR (Attack Success Rate) and Logic Security Score against the previous scan.

    Automatically fails the pipeline (exit 1) if security degrades beyond allowed thresholds.

    Native integration with GitHub Actions.

🎯 Over-Refusal Detection (ORR)

Security shouldn't kill utility. BarkingDog checks if your bot over-refuses legitimate requests. If an auto detailing bot refuses to tell a joke about cars or calculate a 15% discount because it's "too dangerous," BarkingDog marks it as a Utility Failure.
🔁 Daemon Mode

Deploy once, audit forever. BarkingDog can run as a background Docker process, waking up on a schedule to audit your production endpoint and push results to Telegram.
Quick Start
Option 1: Docker (Recommended)

Run a basic security audit:
docker run

-e TARGET_URL=https://your-bot.app/webhook/aegis-scan

-e AEGIS_SECRET_TOKEN=your_secret_token

barkingdog/scanner

Run advanced Red-Teaming audit:
docker run

-e TARGET_URL=https://your-bot.app/webhook/aegis-scan

-e AEGIS_SECRET_TOKEN=your_secret_token

-e AI_API_KEY=sk-...

-e ADVANCED_MODE=true

-e BOT_DOMAIN="Auto Detailing Business"

barkingdog/scanner
Option 2: Python CLI

git clone https://github.com/yourname/barkingdog
cd barkingdog
pip install -r requirements.txt
Run scan

python main.py --url https://your-bot.app/webhook/aegis-scan --advanced
Bot Integration (FastAPI Example)

Add an isolated aegis-scan endpoint to your bot. This prevents security scans from polluting real user analytics or triggering real CRM actions.

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
# 1. Shared secret authentication
expected_token = os.getenv("AEGIS_SECRET_TOKEN")
if not request.token or request.token != expected_token:
return AegisScanResponse(reply="Unauthorized")

# 2. Isolated session per test case
scan_session_id = f"aegis_scan_{uuid.uuid4().hex[:8]}"

# 3. Direct query to the AI Brain
ai_response = await brain.ask(
    user_id=scan_session_id,
    user_message=request.message
)
return AegisScanResponse(reply=ai_response)

Configuration (.env)
Variable	Default	Description
TARGET_URL	—	Your bot's webhook endpoint
AEGIS_SECRET_TOKEN	—	Auth token for scanner access
ADVANCED_MODE	false	Enables LLM Fuzzing, Crescendo, and AI Judge
AI_API_KEY	—	OpenAI key for Advanced features
BOT_DOMAIN	General	Business scope (helps AI Judge accuracy)
SCAN_CONCURRENCY	5	Number of parallel requests
SCAN_DELAY	0.5	Delay between requests (seconds)
CRESCENDO_TURNS	4	Depth of multi-turn attack sequences