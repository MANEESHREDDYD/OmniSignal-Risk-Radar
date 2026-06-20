from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:3000"


def npm_command() -> str:
    return "npm.cmd" if os.name == "nt" else "npm"


def wait_for(url: str, timeout: float = 30.0) -> bytes:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return response.read()
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last_error = exc
            time.sleep(0.4)
    raise RuntimeError(f"Timed out waiting for {url}: {last_error}")


def request_json(
    url: str,
    method: str = "GET",
    body: dict | None = None,
    headers: dict[str, str] | None = None,
):
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.loads(response.read())


def stop_process(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    else:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


def main() -> int:
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=ROOT / "backend",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    frontend = subprocess.Popen(
        [npm_command(), "start", "--", "--hostname", "127.0.0.1", "--port", "3000"],
        cwd=ROOT / "frontend",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    try:
        wait_for(f"{BACKEND_URL}/api/health")
        page = wait_for(FRONTEND_URL)
        cors_request = urllib.request.Request(
            f"{BACKEND_URL}/api/radar/summary",
            headers={"Origin": FRONTEND_URL},
        )
        with urllib.request.urlopen(cors_request, timeout=5) as cors_response:
            assert cors_response.headers["access-control-allow-origin"] == FRONTEND_URL
            summary = json.loads(cors_response.read())
        notifications = request_json(f"{BACKEND_URL}/api/notifications")
        target = next(item for item in notifications if item["status"] == "delivered")
        snoozed = request_json(
            f"{BACKEND_URL}/api/notifications/{target['id']}/snooze",
            method="POST",
            body={},
        )
        audit = request_json(f"{BACKEND_URL}/api/audit")
        assert summary["messages_analyzed"] == 80
        assert summary["accounts_monitored"] == 6
        assert snoozed["status"] == "snoozed"
        assert any(entry["target_id"] == target["id"] for entry in audit)
        assert b"OmniSignal" in page
        request_json(f"{BACKEND_URL}/api/connections/demo-seed?force=true", method="POST")
        print("Backend health: PASSED")
        print("Frontend HTTP 200: PASSED")
        print("Browser CORS policy: PASSED")
        print("80-message / 6-account summary: PASSED")
        print("Notification mutation: PASSED")
        print("Audit-log mutation evidence: PASSED")
        print("Smoke test: PASSED")
        return 0
    finally:
        stop_process(frontend)
        stop_process(backend)


if __name__ == "__main__":
    raise SystemExit(main())
