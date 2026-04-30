<div align="center">
  <img src="assets/reportphoto.jpg" alt="BarkingDog HTML Report Dashboard" width="800">
  <br><br>
  <a href="http://htmlpreview.github.io/?https://github.com/ТВОЙ_НИК/barkingdog/blob/main/assets/report.html">
    <img src="https://img.shields.io/badge/Demo-View_Live_Report-brightgreen?style=for-the-badge&logo=html5" alt="Live Report">
  </a>
</div>

# 🐶 BarkingDog — AI Security Scanner for Telegram Bots & Web Apps


🐶 BarkingDog — единственный сканер, который ломает твоего бота 
так, как это сделает реальный пользователь: через production webhook, 
Telegram-интерфейс, и 4-ходовой roleplay. docker run — и отчёт готов.
Пока инструменты вроде Ragas измеряют *качество*, BarkingDog отвечает на другой вопрос:



## 📸 Примеры работы (Real-World Examples)


### 1. Критический пробой (Security Fail: Jailbreak Success)
![Пример успешного джейлбрейка](assets/fail.jpg)
> Злоумышленник попросил бота составить «образовательный план сценария» о студенте-химике. Базовые фильтры безопасности LLM пропустили запрос из-за "академического" контекста, и бот автомойки выдал детальную инструкцию по подготовке к синтезу запрещенных веществ. BarkingDog автоматически выявил этот обход.
![Пример успешного джейлбрейка](assets/fail2.jpg)
> > Бот автомойки написал полностью рабочий вредоносный код на Python. Он добавил туда перехват клавиатуры, логирование в файл user_input.log и функцию simulate_data_transfer с использованием сокетов (socket.AF_INET) для отправки перехваченных паролей и данных на удаленный сервер. Бот даже приложил код сервера для приема этих данных!
![Пример успешного джейлбрейка](assets/fail3.jpg)
> >ИИ выдал профессиональный гайд по созданию шпионского ПО. Он не только расписал методы сбора (Polling vs. Event-Driven), но и прямо посоветовал использовать конкретные хакерские библиотеки: psutil (для метрик системы), pynput (для перехвата кликов мыши и нажатий клавиш) и scapy (для перехвата и анализа сетевых пакетов).



### 2. Дефект бизнес-логики (Behavior Fail: Roleplay Drift)


![Пример потери роли](assets/behaviorfail.jpg)
> **Контекст:** Атака типа `Crescendo / Roleplay`. Бот не выдал секретных данных, но полностью забыл свою бизнес-цель. Вместо бронирования услуг автомойки, он поддался на уговоры пользователя и начал детально расписывать сценарий криминального триллера об ограблении. BarkingDog фиксирует это как дефект полезности (Behavior Fail), так как бот тратит ресурсы компании на нецелевой контент.
![Пример потери роли](assets/behavior2.jpg)

> >Бот выдал детальную лекцию по синтезу взрывчатки (он сам описал их как "вещества, которые быстро высвобождают энергию при разложении или горении"). Бот рассказал про синтез прекурсоров из "окислителей и топлива", изоляцию через кристаллизацию/дистилляцию и стабилизацию в инертной атмосфере (азот или аргон).

В 2023 году пользователь заставил ChatGPT-бота автодилера продать 
$76,000 автомобиль за $1 через специальный промпт. 
После того как новость распространилась, другие начали эксплуатировать 
ту же уязвимость — дилер был вынужден отключить бота. 


Стандартные фильтры провайдеров не помогают
Исследователи Университета Бен-Гурион показали, что ведущие 
чат-боты, включая ChatGPT, Gemini и Claude, можно вынудить 
генерировать вредоносный контент — угроза описывается как 
"немедленная, ощутимая и крайне тревожная". 


Telegram-боты — специфическая атакуемая поверхность
Каждая третья атака на малый бизнес связана с Telegram-ботами. 
Среднее время простоя сервиса после инцидента — 32 часа. 
Средний финансовый ущерб — $15,000. 

Jailbreak-промпты активно торгуются на форумах
На хакерских форумах появились целые разделы, посвящённые обходу
AI — с конкретными промптами, тактиками roleplay и 
DAN-вариациями. Эксперты отмечают устойчивый рост таких 
обсуждений с 2022 года. Пока разработчик спит, атаки уже 
стандартизированы и масштабированы. Threatshub
---

## 📋 Содержание

- [Зачем BarkingDog](#-зачем-barkingdog)
- [Сравнение с конкурентами](#-сравнение-с-конкурентами)
- [Основные возможности](#-основные-возможности)
- [Быстрый старт](#-быстрый-старт)
- [Интеграция с ботом](#-интеграция-с-ботом-fastapi)
- [Конфигурация](#-конфигурация-env)
- [CI/CD интеграция](#-cicd-автоматизация)
- [Архитектура и модули](#-архитектура-и-модули)
- [Basic Mode](#️-basic-mode-deterministic-evaluation)
- [Advanced Mode](#-advanced-mode-dynamic-mutation--ai-judge)
- [LLM Провайдеры](#-конфигурация-llm-провайдера)
- [Система метрик](#-система-метрик-и-штрафов)
- [Для кого этот инструмент](#-для-кого-этот-инструмент)
- [Roadmap](#-roadmap)

---

## 🎯 Зачем BarkingDog?

Каждое LLM-приложение — потенциальная поверхность атаки. Стандартные фреймворки оценки измеряют качество ответов: faithfulness, context recall, relevancy. BarkingDog закрывает security-пробел через автоматизированное adversarial red teaming.

| Фреймворк | Основной фокус |
|---|---|
| Ragas | Качество RAG (галлюцинации, faithfulness) |
| Promptfoo | Matrix-тестирование и prompt engineering |
| Giskard | Enterprise security платформа (Paid) |
| DeepTeam | 40+ классов уязвимостей, OWASP/NIST маппинг |
| **BarkingDog** | **Production monitoring + Multi-turn Crescendo атаки** |

**Ключевой инсайт:** Простые keyword-фильтры слепы к контексту. Бот может заблокировать прямой запрос «напиши вирус», но сгенерирует вредоносный код, если пользователь обернёт его в 4-ходовой академический roleplay-сценарий. BarkingDog обнаруживает такие логические обходы автоматически.

---



## ⚔️ Сравнение с конкурентами





> **Главное отличие по подходу:** все основные инструменты тестируют модель напрямую через SDK/API провайдера. BarkingDog тестирует **production webhook** — весь стек целиком.






| Критерий | Garak | PyRIT | Promptfoo | Giskard | DeepTeam | **BarkingDog** |
|---|---|---|---|---|---|---|
| Цель тестирования | Модель напрямую | Модель напрямую | Модель / система | LLM-агент | LLM-агент | **Production webhook** |
| Векторов атак | ~100 | Много, гибко | 133 плагина | 50+ проб | 40+ классов | **40+ базовых (сотни с мутациями)** |
| Multi-turn / Crescendo | Слабо | ✅ Сильно | ✅ Есть | ✅ Crescendo, GOAT | ✅ Есть | **✅ Есть** |
| CI/CD интеграция | Есть | С трудом | ✅ Native | Есть | Есть | **✅ GitHub Actions** |
| Daemon / расписание | ❌ | ❌ | ❌ | ❌ | ❌ | **✅ Уникально** |
| Telegram-уведомления | ❌ | ❌ | ❌ | ❌ | ❌ | **✅ Уникально** |
| Over-Refusal Detection | ❌ | ❌ | Частично | Частично | ❌ | **✅ Есть** |
| Domain-aware AI Judge | ❌ | ❌ | ❌ | Частично | ❌ | **✅ Есть** |
| OWASP/NIST маппинг | ❌ | Частично | ✅ | ✅ | ✅ | **✅ OWASP LLM Top 10** |
| Развёртывание | pip/CLI | pip/CLI | npm/CLI | pip/CLI | pip | **Docker (проще всех)** |

**Вывод:** BarkingDog занимает уникальную нишу — **непрерывный production monitoring с готовым маппингом на стандарты OWASP для владельцев ботов без DevSecOps команды**.



---






## 🚀 Основные возможности

### 🧩 Open-Source и Полная Расширяемость (Zero Vendor Lock-in)
В отличие от закрытых enterprise-платформ, BarkingDog имеет полностью открытую и модульную архитектуру. Вы можете легко добавлять собственные специфичные векторы атак в `checks.yaml`, писать кастомные пайплайны обфускации или подключать собственные локальные LLM-модели (через Ollama).

### 🛡️ Двухуровневая архитектура

**1. BASIC Mode — Smoke Testing (бесплатно)**
- Быстрая детерминированная оценка через Regex и keyword matching
- Мгновенное обнаружение явных утечек (пароли, API-ключи, PII)
- **Zero token cost** — идеально для каждого коммита в CI/CD

**2. ADVANCED Mode (`-a` flag)**
- **Dynamic Fuzzing (LLM Mutator):** генерирует уникальные семантические вариации и Base64-пейлоады для обхода статических фильтров
- **Multi-turn / Crescendo Attacks:** эмулирует сложных хакеров, постепенно отравляя контекстное окно LLM через ролевые игры и context poisoning
- **AI Judge (Domain Grounding):** анализирует намерение и контекст на основе вашего `BOT_DOMAIN`, минимизируя false positives

### 📈 CI/CD Regression Tracking
- Сравнивает текущий ASR и Security Score с предыдущим сканом
- Автоматически роняет пайплайн (`exit 1`) при деградации защиты
- Нативная интеграция с GitHub Actions

### 🎯 Over-Refusal Detection (ORR)
Безопасность не должна убивать полезность. BarkingDog проверяет, не стал ли бот "параноиком". Если бот автосервиса отказывается рассчитать скидку 15% как "опасный запрос" — это **Utility Failure**, и он его обнаружит.

### 🔁 Daemon Mode
Разверни раз — аудит навсегда. BarkingDog запускается как фоновый Docker-процесс, просыпается по расписанию и присылает отчёт в Telegram.
<br>
<img src="assets/telegram.jpg" alt="Telegram Notification Example" width="350">

---
### ⚡ Быстрый старт
Вариант 1: Cloud (любой PaaS с поддержкой Docker)

Можно запустить сервис без локального Docker — напрямую из образа в любой PaaS (Railway, Render, Fly.io и др.).

Шаги
Создай новый сервис / проект
Выбери Deploy from Docker Image
Укажи образ:
peternsk/barkingdog
Добавь переменные окружения:
TARGET_URL=https://your-bot.app/webhook/aegis-scan
AEGIS_SECRET_TOKEN=your_secret_token
Запусти деплой
### Вариант 2: Docker (рекомендуется)

**Базовый security-аудит:**
```bash
docker run \
  -e TARGET_URL=[https://your-bot.app/webhook/aegis-scan](https://your-bot.app/webhook/aegis-scan) \
  -e AEGIS_SECRET_TOKEN=your_secret_token \
  peternsk/barkingdog
```

**Advanced Red-Teaming аудит:**
```bash
docker run \
  -e TARGET_URL=[https://your-bot.app/webhook/aegis-scan](https://your-bot.app/webhook/aegis-scan) \
  -e AEGIS_SECRET_TOKEN=your_secret_token \
  -e AI_API_KEY=sk-... \
  -e ADVANCED_MODE=true \
  -e BOT_DOMAIN="PROFILE_OF_YOU_BOT" \
  peternsk/barkingdog
```

### Вариант 2: Python CLI

```bash
git clone https://github.com/yourname/barkingdog
cd barkingdog
pip install -r requirements.txt

# Запуск сканирования
python main.py --url https://your-bot.app/webhook/aegis-scan --advanced
```

---

## 🔌 Интеграция с ботом (FastAPI)

Добавь изолированный `aegis-scan` эндпоинт в своего бота. Это предотвращает загрязнение реальной аналитики и не триггерит CRM-действия во время сканирования.

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
    # 1. Аутентификация по shared secret
    expected_token = os.getenv("AEGIS_SECRET_TOKEN")
    if not request.token or request.token != expected_token:
        return AegisScanResponse(reply="Unauthorized")

    # 2. Изолированная сессия на каждый тест-кейс
    scan_session_id = f"aegis_scan_{uuid.uuid4().hex[:8]}"

    # 3. Прямой запрос к AI-ядру бота
    ai_response = await brain.ask(
        user_id=scan_session_id,
        user_message=request.message
    )
    return AegisScanResponse(reply=ai_response)
```

Если твой бот работает на Long Polling (без Webhooks)

Если твой бот работает через метод опроса (например, bot.polling() или dp.start_polling()), у него нет открытого порта для приема HTTP-запросов от сканера.

Решение простое: поднять минималистичный FastAPI-сервер в фоновом потоке. Это создаст мост для сканера BarkingDog, не ломая работу основного Telegram-бота.
Python

import threading
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

# 1. Твоя основная функция генерации ответа ИИ (которую использует бот)
async def ask_bot_brain(prompt: str) -> str:
    # Здесь вызов OpenAI, Anthropic, локальной модели и т.д.
    return "Ответ от ИИ"

# 2. Создаем фоновый API-сервер для сканера
scan_app = FastAPI()

class AegisScanRequest(BaseModel):
    message: str
    token: str = None

@scan_app.post("/webhook/aegis-scan")
async def aegis_scan_endpoint(request: AegisScanRequest):
    # Проверка секретного токена
    if request.token != os.getenv("AEGIS_SECRET_TOKEN", "secret123"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Прогоняем хакерский промпт через "мозги" бота
    answer = await ask_bot_brain(request.message)
    return {"reply": answer}

# 3. Функция запуска сервера
def run_scanner_api():
    # Запускаем на порту 8000
    uvicorn.run(scan_app, host="0.0.0.0", port=8000, log_level="warning")

# 4. Твоя главная функция запуска бота
def main():
    # Запускаем API для сканера в отдельном фоновом потоке!
    threading.Thread(target=run_scanner_api, daemon=True).start()
    
    print("Бот запущен. Сканер BarkingDog может стучаться на порт 8000.")
    
    # Запуск поллинга твоего Telegram бота
    # bot.polling(none_stop=True) 
    # или await dp.start_polling(bot)







**Почему это важно:** изолированный эндпоинт гарантирует, что тесты безопасности не попадут в аналитику реальных пользователей и не вызовут нежелательных действий в CRM или базе данных.

---

## ⚙️ Конфигурация (.env)



| Переменная | По умолчанию           | Описание |
|---|------------------------|---|
| `TARGET_URL` | —                      | Webhook-эндпоинт тестируемого бота |
| `AEGIS_SECRET_TOKEN` | —                      | Auth-токен для авторизации сканера на целевом боте |
| `BOT_DOMAIN` | `General`              | Бизнес-контекст бота (помогает AI Judge выявлять ролевой дрифт) |
| `DAEMON_MODE` | `true`                     | Включает непрерывное фоновое сканирование (режим агента) |
| `SCAN_INTERVAL_HOURS`| `168`                  | Частота сканирований в часах для Daemon Mode (168 = раз в неделю) |
| `SCAN_CONCURRENCY` | `5`                    | Максимальное количество параллельных асинхронных запросов |
| `SCAN_DELAY` | `0.5`                  | Пауза (в секундах) между запросами для защиты от rate-лимитов |
| `TELEGRAM_BOT_TOKEN` | —                      | API-токен Telegram-бота, который будет рассылать отчеты |
| `TELEGRAM_CHAT_ID` | —                      | ID вашего чата или группы в Telegram для получения результатов |
| `LLM_PROVIDER` | `openai`               | Провайдер ИИ-судьи и мутатора: `openai` / `anthropic` / `ollama` |
| `LLM_MODEL` | `gpt-4o`               | Название модели для выбранного провайдера |
| `AI_API_KEY` | —                      | API-ключ выбранного провайдера (не требуется для Ollama) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL локального Ollama-сервера (если используется) |



## 🚀 CI/CD Автоматизация
BarkingDog поддерживает автоматическую интеграцию в любой CI/CD пайплайн. При деградации метрик сканер возвращает код ошибки `exit 1`, автоматически блокируя деплой уязвимого бота.
<br>
<img src="assets/cdci.jpg" alt="Terminal Output" width="800">

1. **Trigger:** репозиторий вашего бота отправляет `repository_dispatch` после успешного деплоя
2. **Execution:** BarkingDog получает сигнал, собирает Docker-окружение и запускает аудит
3. **Reporting:** HTML-отчёт сохраняется в артефактах GitHub Actions + опциональная отправка в Telegram

### Шаг 1: Настройка бота (отправитель)

Добавь в репозиторий бота `.github/workflows/trigger-scan.yml`:

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

### Шаг 2: Настройка BarkingDog (получатель)

Установи следующие секреты в репозитории BarkingDog:

| Secret | Описание                                          |
|---|---------------------------------------------------|
| `TARGET_URL` | Публичный URL тестируемого бота                   |
| `AI_API_KEY` | API-ключ LLM-провайдера (для AI Judge и Mutators) |
| `AEGIS_SECRET_TOKEN` | Auth-токен для авторизации сканера и бота         |
| `TELEGRAM_BOT_TOKEN` | *(Опционально)* Токен для Telegram-уведомлений    |
| `TELEGRAM_CHAT_ID` | *(Опционально)* ID чата/группы в Telegram         |

**Параметры воркфлоу:**
- **Триггер:** `repository_dispatch` (event type: `bot_updated`)
- **Окружение:** Dockerized Python 3.11-slim
- **Хранение артефактов:** 14 дней

---
## 🧰 Архитектура и движок

BarkingDog использует асинхронный двухуровневый конвейер (Pipeline) для тестирования:

1. **Basic Phase (Triage):** Детерминированный прогон на основе регулярных выражений (`core/evaluator.py`). Отсекает сетевые ошибки, тайм-ауты и очевидные отказы бота (Zero cost).
2. **Advanced Phase (LLM & Crescendo):** Генерация семантических мутаций (`core/mutator_llm.py`), многошаговые атаки с отравлением контекста (`core/mutator_crescendo.py`) и семантическая оценка ответа ИИ-судьей (`core/advanced_evaluator.py`).

Метрики (ASR, BDR, Security Score) рассчитываются на основе взвешенной системы штрафов с применением правила **«честного знаменателя»** (сетевые ошибки 502 не занижают оценку безопасности).

👉 **[Читать подробную документацию по архитектуре, модулям и алгоритмам расчетов ➡️](ARCHITECTURE.md)**



## 👤 Для кого этот инструмент

### ✅ Основная аудитория (ICP)

**Инди-разработчик или малый бизнес с Telegram-ботом на LLM** — построил чат-бота для автосервиса, юридической консультации, онлайн-школы. Не имеет DevSecOps инженера. Хочет знать: "меня нельзя взломать?" Именно им нужен `docker run` и отчёт в Telegram, а не 100 векторов атак в CLI.

**Вторичные сегменты:**
- AI/LLM стартапы на ранней стадии (1–5 человек), которые хотят добавить security в CI без найма security-инженера
- Фрилансеры и AI-агентства, которые сдают LLM-ботов клиентам и хотят добавить "security audit" в пакет услуг
- AI QA инженеры, которые ищут готовый инструмент для черновой проверки перед ручным пентестом
### ❌ Для кого не подходит сейчас

- **Enterprise-корпорации со строгим Compliance (NIST/MITRE):** BarkingDog уже поддерживает детальный маппинг на **OWASP LLM Top 10**, однако интеграция стандартов NIST AI RMF и MITRE ATLAS находится в разработке.
- **Команды с выделенным штатом DevSecOps:** Если у вас есть ресурсы на поддержку и ручную настройку таких инструментов, как Garak или PyRIT, они могут дать более широкое (но менее автоматизированное) покрытие специфических атак.
- **Security-исследователи (Academic Red Teaming):** Инструмент сфокусирован на защите бизнес-логики и продакшена, а не на поиске фундаментальных уязвимостей в архитектуре самих нейросетей (Model Theft, Training Data Poisoning).
---

## 🗺️ Roadmap

### 🔴 Критично (делает проект серьёзным)

- [ ] **Расширить `checks.yaml` до 100 тест-кейсов** — основная слабость. Добавить категории: RAG poisoning, indirect injection, system prompt extraction, off-topic manipulation

- [ ] **NIST RMF / MITRE ATLAS маппинг** — открывает enterprise-аудиторию
- [ ] **Прямой режим через OpenAI/Anthropic SDK** — тестирование моделей без бота

### 🟡 Важно (делает продукт удобным)

- [ ] **Интерактивный HTML-отчёт** — drill-down по категориям, фильтрация по severity
- [ ] **Web UI (Streamlit)** — запуск сканов без CLI для нетехнических пользователей
- [ ] **Поддержка session_id** — для ботов с серверным хранением контекста
- [ ] **Unit/integration тесты** — покрытие `core/evaluator.py` и `core/schemas.py`

### 🟢 Стратегически

- [ ] **Пресеты по доменам** — готовые тест-кейсы для "Legal Bot", "E-commerce Bot", "HR Bot"
- [ ] **Интеграция с Langfuse/LangSmith** — как источник traces для тестирования
- [ ] **Кластеризация fail-ов по первопричине** — группировка инцидентов, а не просто список
- [ ] **RAG-специфичные атаки** — document poisoning, indirect prompt injection через retrieved context
- [ ] **Агентные векторы** — tool abuse, SSRF, privilege escalation

---

## 🤝 Contributing

Проект в активной разработке. Issues и PR приветствуются, особенно:
- Новые тест-кейсы для `checks.yaml`
- Интеграции с новыми LLM-провайдерами
- Улучшения HTML-отчёта

---

## 📄 Лицензия

MIT License — используй свободно, ссылка на проект приветствуется.

---

<div align="center">

**🐶 BarkingDog — потому что хороший охранник лает до того, как взломали, а не после.**

</div>