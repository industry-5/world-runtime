import json
import platform
import socket
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
LOCALHOST = "127.0.0.1"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind((LOCALHOST, 0))
        return int(probe.getsockname()[1])


def _request_json(method: str, url: str, payload: Optional[dict] = None, timeout: float = 10.0):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def _wait_until(description: str, check, timeout: float = 20.0, interval: float = 0.2):
    deadline = time.time() + timeout
    last_error = None
    while time.time() < deadline:
        try:
            value = check()
            if value:
                return value
        except Exception as exc:  # noqa: BLE001
            last_error = exc
        time.sleep(interval)
    detail = f" ({last_error})" if last_error else ""
    raise TimeoutError(f"Timed out waiting for {description}{detail}")


class _Process:
    def __init__(self, cmd: List[str]):
        self._cmd = cmd
        self.proc = None

    def start(self):
        self.proc = subprocess.Popen(  # noqa: S603
            self._cmd,
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def stop(self):
        if not self.proc:
            return
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=5)


class WebDriverSession:
    def __init__(self, driver_base_url: str, session_id: str):
        self.driver_base_url = driver_base_url.rstrip("/")
        self.session_id = session_id

    @classmethod
    def create(cls, driver_base_url: str):
        status, payload = _request_json(
            "POST",
            f"{driver_base_url.rstrip('/')}/session",
            {
                "capabilities": {
                    "alwaysMatch": {
                        "browserName": "safari",
                    }
                }
            },
            timeout=25,
        )
        if status != 200 or "sessionId" not in payload:
            raise RuntimeError(f"Failed to create WebDriver session: {payload}")
        return cls(driver_base_url, payload["sessionId"])

    def _execute(self, endpoint: str, payload: Dict):
        _, result = _request_json(
            "POST",
            f"{self.driver_base_url}/session/{self.session_id}/{endpoint}",
            payload,
            timeout=20,
        )
        return result.get("value")

    def navigate(self, url: str):
        self._execute("url", {"url": url})

    def eval(self, script: str, args: Optional[List] = None):
        return self._execute("execute/sync", {"script": script, "args": args or []})

    def wait_for_js(self, script: str, timeout: float = 20.0, args: Optional[List] = None):
        return _wait_until(
            "browser JS condition",
            lambda: self.eval(script, args=args or []),
            timeout=timeout,
            interval=0.2,
        )

    def quit(self):
        req = urllib.request.Request(
            f"{self.driver_base_url}/session/{self.session_id}",
            method="DELETE",
        )
        try:
            urllib.request.urlopen(req, timeout=5).read()  # noqa: S310
        except Exception:  # noqa: BLE001
            pass


@pytest.fixture(scope="module")
def browser_env():
    if platform.system() != "Darwin":
        pytest.skip("Safari WebDriver E2E is only supported on macOS.")

    try:
        api_port = _free_port()
        studio_port = _free_port()
        driver_port = _free_port()
    except PermissionError:
        pytest.skip("Socket binding is not available in this environment.")

    api = _Process(["python3", "-m", "api.http_server", "--host", LOCALHOST, "--port", str(api_port)])
    studio = _Process(
        [
            "python3",
            "labs/world_game_studio_next/server.py",
            "--host",
            LOCALHOST,
            "--port",
            str(studio_port),
            "--upstream",
            f"http://{LOCALHOST}:{api_port}",
        ]
    )
    driver = _Process(["safaridriver", "--port", str(driver_port)])

    api.start()
    studio.start()
    driver.start()

    try:
        _wait_until(
            "api server",
            lambda: _request_json("GET", f"http://{LOCALHOST}:{api_port}/health", timeout=2)[0] == 200,
            timeout=25,
        )
        _wait_until(
            "studio server",
            lambda: urllib.request.urlopen(f"http://{LOCALHOST}:{studio_port}", timeout=2).status == 200,  # noqa: S310
            timeout=25,
        )
        _wait_until(
            "safaridriver status",
            lambda: _request_json("GET", f"http://{LOCALHOST}:{driver_port}/status", timeout=2)[0] == 200,
            timeout=25,
        )
        try:
            browser = WebDriverSession.create(f"http://{LOCALHOST}:{driver_port}")
        except Exception as exc:  # noqa: BLE001
            pytest.skip(f"Safari WebDriver session unavailable: {exc}")

        root_url = f"http://{LOCALHOST}:{studio_port}"
        browser.navigate(root_url)
        browser.wait_for_js("return Boolean(document.querySelector('#studio-shell'));", timeout=30)
        yield {"browser": browser, "root_url": root_url}
    finally:
        try:
            if "browser" in locals():
                browser.quit()
        finally:
            driver.stop()
            studio.stop()
            api.stop()


def _send_alt_shortcut(browser: WebDriverSession, key: str):
    browser.eval(
        """
        const shortcut = arguments[0];
        window.dispatchEvent(
          new KeyboardEvent("keydown", {
            key: shortcut,
            altKey: true,
            bubbles: true,
            cancelable: true
          })
        );
        return window.location.hash;
        """,
        [key],
    )


def test_wg_p10_browser_e2e_routes_keyboard_and_accessibility(browser_env):
    browser: WebDriverSession = browser_env["browser"]
    root_url = browser_env["root_url"]

    browser.navigate(root_url)
    browser.wait_for_js("return Boolean(document.querySelector('#onboarding-start'));")

    expected = [("2", "#/plan"), ("4", "#/compare"), ("5", "#/replay"), ("6", "#/facilitate"), ("1", "#/onboard")]
    for key, route_hash in expected:
        _send_alt_shortcut(browser, key)
        browser.wait_for_js("return window.location.hash === arguments[0];", timeout=10, args=[route_hash])
        assert browser.eval("return window.location.hash;") == route_hash

    reduced_before = browser.eval(
        "return document.querySelector('#studio-shell').classList.contains('reduced-motion');"
    )
    _send_alt_shortcut(browser, "m")
    browser.wait_for_js(
        "return document.querySelector('#studio-shell').classList.contains('reduced-motion') !== arguments[0];",
        timeout=10,
        args=[reduced_before],
    )
    reduced_after = browser.eval(
        "return document.querySelector('#studio-shell').classList.contains('reduced-motion');"
    )
    assert reduced_before != reduced_after


def test_wg_p10_browser_e2e_map_compare_replay_facilitate_and_profiling(browser_env):
    browser: WebDriverSession = browser_env["browser"]
    root_url = browser_env["root_url"]

    browser.navigate(f"{root_url}#/plan")
    browser.wait_for_js("return window.location.hash === '#/plan';")
    browser.wait_for_js(
        "const select = document.querySelector('#scenario-select'); return Boolean(select && select.options.length);",
        timeout=30,
    )

    browser.eval("document.querySelector('#session-create')?.click(); return true;")
    browser.eval("document.querySelector('#scenario-load')?.click(); return true;")
    browser.wait_for_js(
        "return Boolean(document.querySelector('#world-canvas-root .dymaxion-region-boundary'));",
        timeout=30,
    )

    selected_region = browser.eval(
        """
        const region = document.querySelector('#world-canvas-root .dymaxion-region-boundary');
        if (!region) return null;
        region.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
        return region.getAttribute('data-region-id');
        """
    )
    assert selected_region
    browser.wait_for_js(
        "return document.querySelector('#planning-selection-summary')?.textContent.includes(arguments[0]);",
        timeout=15,
        args=[selected_region],
    )

    toggled = browser.eval(
        """
        const toggle = document.querySelector('#planning-layer-toggles input[data-layer-id]');
        if (!toggle) return false;
        toggle.click();
        return true;
        """
    )
    assert toggled is True

    browser.navigate(f"{root_url}#/compare")
    browser.wait_for_js("return !document.querySelector('.compare-workspace')?.hidden;", timeout=10)
    browser.eval("document.querySelector('#compare-run')?.click(); return true;")

    browser.navigate(f"{root_url}#/replay")
    browser.wait_for_js("return !document.querySelector('.replay-workspace')?.hidden;", timeout=10)
    browser.eval(
        """
        const slider = document.querySelector('#replay-cursor');
        if (!slider) return false;
        slider.value = slider.max || '0';
        slider.dispatchEvent(new Event('input', { bubbles: true }));
        return true;
        """
    )

    browser.navigate(f"{root_url}#/facilitate")
    browser.wait_for_js("return window.location.hash === '#/facilitate';", timeout=10)
    browser.wait_for_js(
        "return !document.querySelector('#planning-facilitation-group')?.hidden && !document.querySelector('#planning-queue-group')?.hidden;",
        timeout=10,
    )
    browser.eval("document.querySelector('#planning-refresh-continuity')?.click(); return true;")

    diagnostics = browser.eval("return window.__WG_STUDIO_NEXT_DIAGNOSTICS || null;")
    assert isinstance(diagnostics, dict)
    assert "budgets_ms" in diagnostics
    assert "map_redraw" in diagnostics
    assert "overlay_toggle" in diagnostics
    assert "replay_scrub" in diagnostics
    assert diagnostics["map_redraw"]["sample_count"] > 0
    assert diagnostics["overlay_toggle"]["sample_count"] > 0

    for metric_name, budget_name in [
        ("map_redraw", "map_redraw_p95"),
        ("overlay_toggle", "overlay_toggle_p95"),
        ("replay_scrub", "replay_scrub_p95"),
    ]:
        sample = diagnostics[metric_name]
        if sample["sample_count"] > 0 and sample["p95_ms"] is not None:
            assert sample["p95_ms"] <= diagnostics["budgets_ms"][budget_name]
