# ATLAS 7.0 — AI Personal Assistant

**Atlas 7.0** is an advanced, feature-rich AI personal assistant for Windows with a React-based HUD (Iron Man style) interface. It combines voice interaction, computer vision, system automation, machine learning, and multi-agent orchestration into a single cohesive platform.

---

## Features Overview

### Core AI
- **AI Engine** — Multi-LLM support (Groq, Gemini, Ollama), intelligent routing
- **Voice Input** — Wake word detection ("Atlas"), speech-to-text, continuous listening
- **Voice Output** — Text-to-speech with Edge TTS (Bengali + English)
- **Intent Classification** — 46+ intents, natural language understanding
- **Context Engine** — Short-term memory, long-term SQLite memory, vector DB (ChromaDB)
- **Language Detection** — Automatic Bengali/English detection

### Authentication & Security
- Face recognition authentication (anti-spoofing)
- Voice biometric authentication
- PIN-based authentication
- Session management, guest mode, intruder alerts
- Privacy guard, lock screen

### Multi-Agent System (`backend/agent/`)
| Agent | Purpose |
|---|---|
| **PCAgent** | System control, shutdown/restart/lock, battery, WiFi, Bluetooth, process manager, startup apps, PC optimization |
| **FileAgent** | File/folder CRUD, search, organize downloads, disk usage |
| **WebAgent** | Web search, research, URL opener, summarization |
| **MediaAgent** | YouTube search/play, image generation, meme creation |
| **AppAgent** | Open desktop/web applications |
| **TerminalAgent** | Terminal command execution with safety checks (dangerous pattern blocking) |
| **BrowserAgent** | Playwright-powered browser automation (click, type, scroll, fill forms, tabs) |
| **SecurityAgent** | Breach check, privacy mode, password strength |
| **ProductivityAgent** | Task management, Pomodoro timer, reminders |
| **ActionAgent** | Routes voice commands to 14 action modules |
| **AutomationAgent** | API testing, bug finding, clipboard, git, news, price tracking, WhatsApp |
| **MLAgent** | Zero-code ML: dataset loading, training, prediction, visualization, AutoML |

### Action Modules (`backend/action/`)
- Browser control, computer control, desktop management
- File controller, file processor, code helper, dev agent
- Web search, YouTube video, flight finder
- Reminder, game updater, open app, computer settings

### Agent2 — Task Pipeline (`backend/agent2/`)
- **Planner** — AI-powered goal decomposition into step-by-step plans
- **Executor** — Executes multi-step plans with error recovery & auto-fix
- **Task Queue** — Background task queue with priority, status tracking
- **Error Handler** — Automatic error analysis, retry/skip/replan decisions
- **Command Handler** — Routes complex commands to agent2 pipeline

### Automation (`backend/automation/`)
- API endpoint tester, bug finder, clipboard manager
- Document writer, file organizer, git assistant
- News analyzer, price tracker, screen automation
- Social media monitor, WhatsApp bot

### Computer Vision (`backend/vision/`)
- Screen reader, OCR scanner, object detection
- Face/mood detection, eye tracking, handwriting recognition
- Diagram reader, QR scanner, body language analysis

### System Tools (`backend/system/`)
- CPU, RAM, disk real-time metrics
- Temperature monitoring, RAM optimization, disk health
- Driver checker, internet speed test, gaming mode
- PC health reports, startup manager

### Study & Education (`backend/study/`)
- Flashcards with spaced repetition, exam preparation
- Past paper analysis, note-to-mindmap, concept maps
- YouTube AI integration, teacher mode, citation generator

### Bangladesh Features (`backend/bangladesh/`)
- Bangla OCR, BD news, BD currency converter
- BD stock market, prayer calendar, exam helper

### Productivity (`backend/productivity/`)
- Email manager, calendar manager, PDF reader
- Excel/Word AI, meeting notes, web scraper
- Research assistant, presentation maker, math solver

### Analytics (`backend/analytics/`)
- Personal analytics dashboard, productivity score
- Focus score, study analytics, spending analytics
- Habit predictor, goal probability, weekly reports

### Advanced AI (`backend/advanced/`)
- Digital twin, emotion voice, personality learning
- Predictive engine, self-correction, mood tracking
- Multi-model router, dreams module

### Security (`backend/security/`)
- Malware scanner, network monitor, password manager
- 2FA manager, breach detector, privacy mode
- Self-destruct, screen watermark, fake screen

### Entertainment (`backend/fun/`)
- Story generation, quizzes, language tutor
- Interview preparation, dream analyzer, debates

### Lifestyle (`backend/life/`)
- Workout tracker, sleep tracker, mood tracker
- Stress detector, posture alert, eye rest reminder
- Journal, time capsule, BMI calculator

### Media (`backend/media/`)
- Image generator, video downloader, music player
- Podcast creator, subtitle generator, meme generator
- Background remover

---

## Architecture

```
Atlas 7.0/
├── server.py                 ← FastAPI backend (port 8000)
├── config.py                 ← All settings
├── command_handler.py        ← Command routing
├── run.py                    ← One-click launcher
├── main.py                   ← Application entry point
├── or_client.py              ← Ollama client
├── requirements.txt          ← Python dependencies
├── .env                      ← API keys (gitignored!)
│
├── backend/
│   ├── core/                 ← AI Engine, Voice, Memory, Context, Parser
│   ├── auth/                 ← Face, Voice, PIN auth + security
│   ├── agent/                ← Multi-agent orchestrator (PC, File, Web, etc.)
│   ├── agent2/               ← Task planner, executor, queue
│   ├── action/               ← Action execution layer (browser, files, etc.)
│   ├── automation/           ← API tester, git, WhatsApp, clipboard, etc.
│   ├── command_handlers/     ← 18+ specialized command handlers
│   ├── system/               ← System metrics, optimization, health
│   ├── vision/               ← OCR, object detection, face mood, etc.
│   ├── study/                ← Flashcards, exam prep, citation gen
│   ├── productivity/         ← Email, calendar, PDF, research
│   ├── security/             ← Malware scan, password manager, 2FA
│   ├── analytics/            ← Productivity/focus scores, habit prediction
│   ├── bangladesh/           ← BD news, currency, prayer calendar
│   ├── advanced/             ← Digital twin, emotion, self-correction
│   ├── media/                ← Image/video/music processing
│   ├── fun/                  ← Quizzes, stories, debate
│   └── life/                 ← Workout, sleep, mood, journal
│
├── frontend/                 ← React app (port 5173)
│   ├── src/
│   │   ├── pages/            ← LoginPage, MainPage
│   │   ├── components/
│   │   │   ├── chat/         ← ChatPanel
│   │   │   ├── hud/          ← Iron Man style HUD (TopBar, Bottom, Left, Right, Center)
│   │   │   ├── panels/       ← Analytics, Bangladesh, Media, ML, Security, Study, System
│   │   │   └── ui/           ← Sidebar, TopBar
│   │   ├── store/            ← Zustand state management
│   │   └── services/         ← API service layer
│   └── package.json
│
├── data/                     ← Databases, user profiles
├── logs/                     ← Application logs
└── tools/                    ← Utility tools
```

---

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### Backend Setup
```bash
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

### Environment Variables
Copy `.env.example` to `.env` and add your API keys:
```env
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key
WEATHER_API_KEY=your_weather_key
VIRUSTOTAL_API_KEY=your_virustotal_key
NEWS_API_KEY=your_news_key
```

### Run (Two Terminals)
```bash
# Terminal 1 — Backend
python server.py

# Terminal 2 — Frontend
cd frontend && npm run dev
```

Or launch both together:
```bash
python run.py
```

Or double-click `Atlas.bat` (Windows).

---

## URLs

| Service | URL |
|---|---|
| **App** | http://localhost:5173 |
| **API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |

---

## Voice Commands

Atlas supports **English** and **Bengali** voice commands. Say **"Atlas"** to wake it up.

### System
- "Atlas, shutdown PC" / "পিসি shut down করো"
- "Atlas, optimize my PC" / "পিসি optimize করো"
- "Atlas, battery status" / "বattery কেমন?"
- "Atlas, lock the system" / "সিস্টেম lock করো"

### Files
- "Atlas, organize downloads" / "ডাউনলোড organize করো"
- "Atlas, search for report.pdf" / "report.pdf খুঁজো"
- "Atlas, create a new file" / "নতুন file তৈরি করো"

### Web
- "Atlas, search AI news" / "AI news search করো"
- "Atlas, open YouTube" / "YouTube খোলো"
- "Atlas, research quantum computing"

### Media
- "Atlas, play music" / "গান play করো"
- "Atlas, search YouTube for Python tutorial"
- "Atlas, generate an image of a sunset"

### Apps
- "Atlas, open Chrome" / "Chrome খোলো"
- "Atlas, open VS Code" / "VS Code খোলো"
- "Atlas, open Gmail"

### Productivity
- "Atlas, add task 'buy groceries'" / "টাস্ক add করো"
- "Atlas, start Pomodoro 25 minutes"
- "Atlas, show my tasks"

### Terminal
- "Atlas, run git status"
- "Atlas, install pandas with pip"
- "Atlas, ping google.com"

### Bangladesh
- "Atlas, আজকের সংবাদ দেখাও" (Today's news)
- "Atlas, নামাজের সময় দেখাও" (Prayer times)
- "Atlas, টাকা কত?" (Currency rate)

### Multi-Step (Agent2)
- "Create a research document about AI and save it to desktop"
- "Research the weather in Dhaka and write a summary"
- "Find and compare laptop prices online"

---

## Tech Stack

### Backend
- **Framework:** FastAPI
- **AI Models:** Groq (Llama 3), Google Gemini
- **Voice:** SpeechRecognition, Edge TTS, PyAudio
- **Database:** SQLite, ChromaDB (vector)
- **ML:** Scikit-learn, Pandas, NumPy, Joblib
- **Browser Automation:** Playwright
- **Computer Vision:** OpenCV, Pillow
- **System:** Psutil, PyAutoGUI, Winshell

### Frontend
- **Framework:** React 18 + Vite
- **State:** Zustand
- **Styling:** Tailwind CSS
- **UI:** Custom Iron Man HUD components

---

## Building Executable

```bash
python -m PyInstaller Atlas.spec
```

Or use the portable build script:
```bash
.\build_portable.ps1
```

An installer can be generated with Inno Setup using `setup.iss`.

---

## License

MIT License

Copyright (c) 2025-2026 Hridoy

---

## Author

**Hridoy** — [GitHub](https://github.com/hridoy8098)
