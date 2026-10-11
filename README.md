# AI Agentic E-commerce Testing (Python + Playwright + Ollama)
Owner: Srimathi B
A learning project that tests a **local demo shop**. It does not make real purchases.
The AI planner can use a local Ollama model; a deterministic fallback keeps the project runnable if Ollama is not installed.

## What is included
- Local Flask demo shop at `http://127.0.0.1:5000`
- Playwright browser actions and page observations
- Ollama-backed planner (`qwen2.5:3b` suggested) with safe action allow-list
- Pytest scenarios for login, search, cart and checkout
- Custom Extent-style HTML report at `reports/extent-report.html`
- Screenshots for failed test cases

> Note: ExtentReports is primarily a Java reporting library and does not provide an official Python integration comparable to its Java SDK. This project creates a standalone Extent-style HTML report in Python, rather than claiming to use the Java ExtentReports SDK.

## 1. Install prerequisites
- Python 3.10+ (Python 3.11 recommended)
- Google Chrome is not required; Playwright installs its own Chromium.
- For local AI, install Ollama from https://ollama.com/download

Open a terminal in this folder.

### Windows PowerShell
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install chromium
```

If PowerShell blocks activation, use:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
```

### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install chromium
```

## 2. Start the local demo shop
Terminal 1:
```bash
python app.py
```
Open http://127.0.0.1:5000. Demo credentials:
- username: `demo`
- password: `demo123`

All checkout activity is simulated locally.

## 3. (Optional) Set up local AI with Ollama
Install Ollama, then in a separate terminal:
```bash
ollama pull qwen2.5:3b
ollama serve
```
Ollama may already run as a background service. The default API is `http://127.0.0.1:11434`.

PowerShell:
```powershell
$env:OLLAMA_MODEL="qwen2.5:3b"
$env:USE_OLLAMA="1"
```
macOS/Linux:
```bash
export OLLAMA_MODEL=qwen2.5:3b
export USE_OLLAMA=1
```

If you want to run without AI while setting up:
- Windows PowerShell: `$env:USE_OLLAMA="0"`
- macOS/Linux: `export USE_OLLAMA=0`

The AI is restricted to an allow-list of actions. It cannot execute arbitrary Python or arbitrary JavaScript. Review generated plans and never connect an experimental agent to a real store, real account, or payment flow.

## 4. Run tests
With the demo shop running in Terminal 1, use Terminal 2:
```bash
pytest -v
```

The test suite runs the fixed regression tests and an agentic objective test. The agentic test asks the planner to complete a safe local shopping flow. When Ollama is disabled/unavailable, a deterministic plan is used.

To run only the agentic test:
```bash
pytest -v tests/test_agentic_flow.py
```

## 5. View reports
After pytest finishes:
- HTML report: `reports/extent-report.html`
- Failure screenshots: `reports/screenshots/`

Open `reports/extent-report.html` in your browser. The report includes pass/fail status, duration, failure details and captured screenshots where available.

## 6. Project layout
```text
agentic_ecommerce_testing/
├── app.py
├── requirements.txt
├── pytest.ini
├── conftest.py
├── agent/
│   ├── planner.py
│   └── executor.py
├── pages/
│   └── shop_page.py
├── tests/
│   ├── test_regression.py
│   └── test_agentic_flow.py
├── utils/
│   └── extent_report.py
└── reports/
    └── screenshots/
```

## How the agentic loop works
1. **Goal**: a human gives a testing objective.
2. **Plan**: Ollama proposes structured steps in JSON.
3. **Guardrails**: the app validates every action against an allow-list.
4. **Act**: Playwright executes the steps.
5. **Observe**: the agent reads visible page text and URL.
6. **Verify**: assertions check meaningful outcomes; a failure is reported, not silently marked as passed.

## Troubleshooting
- `Executable doesn't exist`: run `python -m playwright install chromium`.
- `Connection refused` to localhost: start `python app.py` first.
- Ollama unavailable: set `USE_OLLAMA=0` or start Ollama; fallback mode is expected.
- AI response isn't valid JSON: planner retries parsing once, then uses a safe fallback plan.
- Port 5000 is busy: set `PORT=5001` and update `BASE_URL` in `pytest.ini` accordingly.
