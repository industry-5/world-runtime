import importlib.util
import io
from pathlib import Path
import types

from core.policy_engine import DeterministicPolicyEngine


REPO_ROOT = Path(__file__).resolve().parents[2]
LAB_DIR = REPO_ROOT / "labs" / "supply_ops_lab"
EXPECTED_OUTCOMES = {
    "allow_recovery": "allow",
    "warn_low_inventory_cover": "warn",
    "require_approval_high_expedite": "require_approval",
    "deny_low_fill_rate": "deny",
}


def _load_server_module():
    spec = importlib.util.spec_from_file_location(
        "supply_ops_lab_server",
        LAB_DIR / "server.py",
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _make_handler(module, *, path, method, service, body=b""):
    recorded = {"status": None, "headers": [], "body": b""}
    handler = module.SupplyOpsLabHandler.__new__(module.SupplyOpsLabHandler)
    handler.path = path
    handler.command = method
    handler.request_version = "HTTP/1.1"
    handler.requestline = f"{method} {path} HTTP/1.1"
    handler.server_version = "SupplyOpsLabTest"
    handler.sys_version = ""
    handler.upstream_base = "http://127.0.0.1:8080"
    handler.service = service
    handler.headers = {"Content-Length": str(len(body)), "Content-Type": "application/json"}
    handler.rfile = io.BytesIO(body)
    handler.wfile = io.BytesIO()

    def send_response(self, status_code, message=None):
        recorded["status"] = status_code

    def send_header(self, key, value):
        recorded["headers"].append((key, value))

    def end_headers(self):
        return None

    handler.send_response = types.MethodType(send_response, handler)
    handler.send_header = types.MethodType(send_header, handler)
    handler.end_headers = types.MethodType(end_headers, handler)
    return handler, recorded


def test_supply_ops_lab_scaffold_exists():
    assert (LAB_DIR / "README.md").exists()
    assert (LAB_DIR / "index.html").exists()
    assert (LAB_DIR / "decision-explorer.html").exists()
    assert (LAB_DIR / "styles.css").exists()
    assert (LAB_DIR / "app.js").exists()
    assert (LAB_DIR / "decision-explorer.js").exists()
    assert (LAB_DIR / "server.py").exists()


def test_supply_ops_lab_server_owns_adapter_and_proxy_boundary():
    server_code = (LAB_DIR / "server.py").read_text(encoding="utf-8")

    assert "class SupplyOpsLabService" in server_code
    assert 'LAB_MILESTONE = "SO-P4"' in server_code
    assert 'requested.startswith("/api/v1/")' in server_code
    assert 'PUBLIC_ENDPOINTS["session_create"]' in server_code
    assert 'PUBLIC_ENDPOINTS["proposal_submit"]' in server_code
    assert 'DECISION_EXPLORER_BOOTSTRAP_ENDPOINT = "/api/supply-ops/decision-explorer/bootstrap"' in server_code
    assert 'DECISION_EXPLORER_EVALUATE_ENDPOINT = "/api/supply-ops/decision-explorer/evaluate"' in server_code
    assert "SupplyOpsTranslator" in server_code
    assert "build_commitment_risk_event" in server_code
    assert "build_recovery_hypothetical_events" in server_code


def test_supply_ops_lab_bootstrap_exposes_all_so_p2_presets():
    module = _load_server_module()
    service = module.SupplyOpsLabService(REPO_ROOT, "http://127.0.0.1:8080")

    bootstrap = service.build_bootstrap_payload()

    assert bootstrap["milestone"] == "SO-P4"
    assert bootstrap["surface"] == "SO-P3 operator/reference route"
    assert bootstrap["default_preset_fixture_name"] == module.REVIEWED_FIXTURE_NAME
    assert [item["fixture_name"] for item in bootstrap["preset_catalog"]] == list(EXPECTED_OUTCOMES)
    assert set(bootstrap["preset_snapshots"]) == set(EXPECTED_OUTCOMES)
    assert bootstrap["startup_guide"]["commands"]
    assert bootstrap["startup_guide"]["smoke_checks"]
    assert bootstrap["parallel_routes"]["decision_explorer"] == "/decision-explorer"
    assert any(
        item["label"] == "Start Supply Ops lab server"
        for item in bootstrap["startup_guide"]["commands"]
    )


def test_supply_ops_lab_reviewed_snapshot_remains_available():
    module = _load_server_module()
    service = module.SupplyOpsLabService(REPO_ROOT, "http://127.0.0.1:8080")

    snapshot = service.build_reviewed_snapshot()

    assert snapshot["fixture_name"] == module.REVIEWED_FIXTURE_NAME
    assert snapshot["preset"]["expected_outcome"] == "require_approval"
    assert snapshot["policy_preview"]["final_outcome"] == "require_approval"
    assert snapshot["scenario_evidence"]["reviewed_example_match"] is True


def test_supply_ops_lab_preset_snapshots_cover_readable_results_and_timeline():
    module = _load_server_module()
    service = module.SupplyOpsLabService(REPO_ROOT, "http://127.0.0.1:8080")

    for fixture_name, expected_outcome in EXPECTED_OUTCOMES.items():
        snapshot = service.build_preset_snapshot(fixture_name)

        assert snapshot["preset"]["fixture_name"] == fixture_name
        assert snapshot["preset"]["expected_outcome"] == expected_outcome
        assert snapshot["proposal_overview"]["headline"]
        assert snapshot["policy_preview"]["final_outcome"] == expected_outcome
        assert snapshot["replay_summary"]["commitment_state"]["status"] == "at_risk"
        assert snapshot["simulation_summary"]["status"] == "completed"
        assert snapshot["simulation_summary"]["projected_late_units_after_action"] >= 0
        assert len(snapshot["timeline"]) >= 6
        assert snapshot["timeline"][0]["stage"] == "preset"
        assert any(item["stage"] == "simulation" for item in snapshot["timeline"])
        assert snapshot["scenario_evidence"]["reviewed_example_match"] is (
            fixture_name == module.REVIEWED_FIXTURE_NAME
        )


def test_supply_ops_lab_run_flow_tracks_selected_preset_without_domain_logic_in_browser(monkeypatch):
    module = _load_server_module()
    service = module.SupplyOpsLabService(REPO_ROOT, "http://127.0.0.1:8080")

    def fake_post_json(path, payload):
        if path == module.PUBLIC_ENDPOINTS["session_create"]:
            return {"session_id": "session.test.supply-ops"}
        if path == module.PUBLIC_ENDPOINTS["proposal_submit"]:
            report = DeterministicPolicyEngine().evaluate_policies(
                payload["policies"],
                payload["proposal"],
            ).as_dict()
            approval = None
            if report["requires_approval"]:
                approval = {"approval_id": "approval.test.supply-ops", "status": "pending"}
            return {
                "proposal_id": payload["proposal"]["proposal_id"],
                "policy_report": report,
                "approval": approval,
            }
        raise AssertionError(f"unexpected path: {path}")

    monkeypatch.setattr(service, "_post_json", fake_post_json)

    result = service.run_preset_flow("require_approval_high_expedite")

    assert result["milestone"] == "SO-P4"
    assert result["fixture_name"] == "require_approval_high_expedite"
    assert result["policy_gate"]["final_outcome"] == "require_approval"
    assert result["policy_summary"]["approval_copy"] == "Approval is pending upstream review."
    assert any(item["stage"] == "approval" for item in result["timeline"])
    assert result["simulation_summary"]["status"] == "completed"


def test_supply_ops_lab_browser_stays_thin_and_server_backed():
    app_code = (LAB_DIR / "app.js").read_text(encoding="utf-8")
    decision_explorer_code = (LAB_DIR / "decision-explorer.js").read_text(encoding="utf-8")
    index_code = (LAB_DIR / "index.html").read_text(encoding="utf-8")
    explorer_html = (LAB_DIR / "decision-explorer.html").read_text(encoding="utf-8")

    assert "/api/supply-ops/bootstrap" in app_code
    assert "/api/supply-ops/run" in app_code
    assert "/api/supply-ops/decision-explorer/bootstrap" in decision_explorer_code
    assert "/api/supply-ops/decision-explorer/evaluate" in decision_explorer_code
    assert "retry-bootstrap" in index_code
    assert "startup-commands" in index_code
    assert "preset-cards" in index_code
    assert "timeline-flow" in index_code
    assert "explorer-plan-cards" in explorer_html
    assert "explorer-weight-controls" in explorer_html
    assert "fetchJson" in app_code
    assert "fetchJson" in decision_explorer_code
    assert "loadBootstrap" in app_code
    assert "renderSelectionPlaceholder" in app_code
    assert "build_recovery_hypothetical_events" not in app_code
    assert "DeterministicPolicyEngine" not in decision_explorer_code
    assert "SupplyOpsTranslator" not in app_code
    assert "DeterministicPolicyEngine" not in app_code


def test_supply_ops_lab_http_smoke_path_covers_health_bootstrap_and_run(monkeypatch):
    module = _load_server_module()
    service = module.SupplyOpsLabService(REPO_ROOT, "http://127.0.0.1:8080")

    def fake_post_json(path, payload):
        if path == module.PUBLIC_ENDPOINTS["session_create"]:
            return {"session_id": "session.test.supply-ops"}
        if path == module.PUBLIC_ENDPOINTS["proposal_submit"]:
            report = DeterministicPolicyEngine().evaluate_policies(
                payload["policies"],
                payload["proposal"],
            ).as_dict()
            approval = None
            if report["requires_approval"]:
                approval = {"approval_id": "approval.test.supply-ops", "status": "pending"}
            return {
                "proposal_id": payload["proposal"]["proposal_id"],
                "policy_report": report,
                "approval": approval,
            }
        raise AssertionError(f"unexpected path: {path}")

    monkeypatch.setattr(service, "_post_json", fake_post_json)
    health_handler, health_recorded = _make_handler(
        module,
        path="/health",
        method="GET",
        service=service,
    )
    health_handler.do_GET()
    assert health_recorded["status"] == 200
    health_payload = health_handler.wfile.getvalue().decode("utf-8")
    assert '"milestone": "SO-P4"' in health_payload
    assert '"supported_path": "preserved SO-P3 operator/reference route plus SO-P4 Decision Explorer concept route"' in health_payload

    bootstrap_handler, bootstrap_recorded = _make_handler(
        module,
        path="/api/supply-ops/bootstrap",
        method="GET",
        service=service,
    )
    bootstrap_handler.do_GET()
    assert bootstrap_recorded["status"] == 200
    bootstrap_payload = bootstrap_handler.wfile.getvalue().decode("utf-8")
    assert '"ok": true' in bootstrap_payload
    assert '"startup_guide"' in bootstrap_payload
    assert '"demo_steps"' in bootstrap_payload

    run_body = (
        b'{"fixture_name": "allow_recovery"}'
    )
    run_handler, run_recorded = _make_handler(
        module,
        path="/api/supply-ops/run",
        method="POST",
        service=service,
        body=run_body,
    )
    run_handler.do_POST()
    assert run_recorded["status"] == 200
    run_payload = run_handler.wfile.getvalue().decode("utf-8")
    assert '"ok": true' in run_payload
    assert '"milestone": "SO-P4"' in run_payload
    assert '"final_outcome": "allow"' in run_payload


def test_supply_ops_lab_decision_explorer_bootstrap_exposes_parallel_surface():
    module = _load_server_module()
    service = module.SupplyOpsLabService(REPO_ROOT, "http://127.0.0.1:8080")

    bootstrap = service.build_decision_explorer_bootstrap_payload()

    assert bootstrap["milestone"] == "SO-P4"
    assert bootstrap["mode"] == "decision_explorer_parallel_concept_surface"
    assert bootstrap["routes"]["decision_explorer"] == "/decision-explorer"
    assert bootstrap["commitment"]["commitment_id"] == "commitment.retailer-4821"
    assert len(bootstrap["proposal_catalog"]) == 3
    assert bootstrap["controls"]["default_request"]["weights"] == module.DECISION_EXPLORER_DEFAULT_WEIGHTS
    assert bootstrap["initial_evaluation"]["selected_plan_id"] == "plan.margin-guardrail"


def test_supply_ops_lab_decision_explorer_service_heavy_weights_flip_selection():
    module = _load_server_module()
    service = module.SupplyOpsLabService(REPO_ROOT, "http://127.0.0.1:8080")

    default_result = service.evaluate_decision_explorer(
        weights=module.DECISION_EXPLORER_DEFAULT_WEIGHTS,
        simulation_mode="include",
    )
    service_heavy_result = service.evaluate_decision_explorer(
        weights=module.DECISION_EXPLORER_SERVICE_HEAVY_WEIGHTS,
        simulation_mode="include",
    )

    assert default_result["selected_plan_id"] == "plan.margin-guardrail"
    assert default_result["plans"][0]["policy_surface"]["final_outcome"] == "allow"
    assert service_heavy_result["selected_plan_id"] == "plan.service-first"
    assert service_heavy_result["selection_changed_from_default"] is True
    assert service_heavy_result["decision_summary"]["policy_shift"] is True
    assert service_heavy_result["plans"][0]["policy_surface"]["final_outcome"] == "require_approval"


def test_supply_ops_lab_decision_explorer_http_endpoints_work():
    module = _load_server_module()
    service = module.SupplyOpsLabService(REPO_ROOT, "http://127.0.0.1:8080")

    bootstrap_handler, bootstrap_recorded = _make_handler(
        module,
        path="/api/supply-ops/decision-explorer/bootstrap",
        method="GET",
        service=service,
    )
    bootstrap_handler.do_GET()
    assert bootstrap_recorded["status"] == 200
    bootstrap_payload = bootstrap_handler.wfile.getvalue().decode("utf-8")
    assert '"ok": true' in bootstrap_payload
    assert '"initial_evaluation"' in bootstrap_payload
    assert '"selected_plan_id": "plan.margin-guardrail"' in bootstrap_payload

    evaluate_handler, evaluate_recorded = _make_handler(
        module,
        path="/api/supply-ops/decision-explorer/evaluate",
        method="POST",
        service=service,
        body=(
            b'{"weights": {"service_level": 70, "margin_guardrail": 15, "approval_friction": 15}, '
            b'"simulation_mode": "include"}'
        ),
    )
    evaluate_handler.do_POST()
    assert evaluate_recorded["status"] == 200
    evaluate_payload = evaluate_handler.wfile.getvalue().decode("utf-8")
    assert '"ok": true' in evaluate_payload
    assert '"selected_plan_id": "plan.service-first"' in evaluate_payload
    assert '"policy_shift": true' in evaluate_payload
