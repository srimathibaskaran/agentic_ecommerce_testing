import html
from datetime import datetime
from pathlib import Path

REPORT_DIR = Path("reports")
SCREENSHOT_DIR = REPORT_DIR / "screenshots"
_RESULTS = []

def pytest_configure(config):
    global _RESULTS
    _RESULTS = []
    REPORT_DIR.mkdir(exist_ok=True)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

def pytest_runtest_makereport(item, call):
    # Save the result on the item so failure screenshots can be attached safely.
    if call.when == "call" and call.excinfo:
        page = item.funcargs.get("browser_page")
        if page:
            try:
                SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
                safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in item.name)
                page.screenshot(path=str(SCREENSHOT_DIR / f"{safe_name}.png"), full_page=True)
            except Exception:
                pass

def pytest_runtest_logreport(report):
    if report.when != "call":
        return
    _RESULTS.append({
        "name": report.nodeid,
        "status": report.outcome.upper(),
        "duration": round(report.duration, 3),
        "details": str(report.longrepr) if report.failed else "",
        "properties": getattr(report, "user_properties", []),
    })

def pytest_sessionfinish(session, exitstatus):
    total = len(_RESULTS)
    passed = sum(r["status"] == "PASSED" for r in _RESULTS)
    failed = sum(r["status"] == "FAILED" for r in _RESULTS)
    skipped = sum(r["status"] == "SKIPPED" for r in _RESULTS)
    rows = []
    for r in _RESULTS:
        status_class = "pass" if r["status"] == "PASSED" else "fail" if r["status"] == "FAILED" else "skip"
        detail = html.escape(r["details"][:5000])
        props = "".join(f"<li><b>{html.escape(str(k))}:</b> {html.escape(str(v))}</li>" for k, v in r["properties"])
        rows.append(f"""
        <tr><td>{html.escape(r['name'])}<ul>{props}</ul></td>
        <td><span class="pill {status_class}">{r['status']}</span></td>
        <td>{r['duration']:.3f}s</td>
        <td><details><summary>View details</summary><pre>{detail or 'No failure details.'}</pre></details></td></tr>""")
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><title>Agentic Test Report</title>
    <style>
    body{{font-family:Arial,sans-serif;margin:28px;color:#222;background:#f5f7fb}}
    header,table{{background:white;border-radius:10px;padding:18px;box-shadow:0 1px 5px #ddd}}
    h1{{margin:0 0 8px}} .cards{{display:flex;gap:12px;flex-wrap:wrap;margin:18px 0}}
    .metric{{background:white;padding:18px;border-radius:8px;min-width:100px;box-shadow:0 1px 5px #ddd}}
    .metric strong{{display:block;font-size:26px}} table{{width:100%;border-collapse:collapse;padding:0}}
    th,td{{padding:12px;text-align:left;border-bottom:1px solid #eee;vertical-align:top}} th{{background:#f0f3f8}}
    .pill{{padding:5px 9px;border-radius:15px;font-size:12px;font-weight:bold}} .pass{{background:#d8f5df;color:#17652c}}
    .fail{{background:#ffe0e0;color:#9b1c1c}} .skip{{background:#fff0c2;color:#765500}} pre{{white-space:pre-wrap;max-width:700px}}
    ul{{padding-left:18px;font-size:12px}}
    </style></head><body><header><h1>Agentic E-commerce Test Report</h1>
    <p>Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p></header>
    <div class="cards"><div class="metric"><strong>{total}</strong>Total</div>
    <div class="metric"><strong>{passed}</strong>Passed</div><div class="metric"><strong>{failed}</strong>Failed</div>
    <div class="metric"><strong>{skipped}</strong>Skipped</div></div>
    <table><thead><tr><th>Test / Metadata</th><th>Status</th><th>Duration</th><th>Details</th></tr></thead>
    <tbody>{''.join(rows) or '<tr><td colspan="4">No test results yet</td></tr>'}</tbody></table>
    <p>Local demo only. This is a Python-generated Extent-style report, not the Java ExtentReports SDK.</p>
    </body></html>"""
    REPORT_DIR.mkdir(exist_ok=True)
    (REPORT_DIR / "extent-report.html").write_text(doc, encoding="utf-8")
