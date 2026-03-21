PYTHON ?= python3
PIP ?= pip3

.PHONY: help install dev test test-verbose schemas examples adapters evals air-traffic-evals validate protocol-compat public-api-compat extension-contracts scaffold-smoke ci-gate release-artifacts release-dry-run fixtures app-client api-server sdk-example workflow-quickstart workflow-failure workflow-proposal workflow-simulation observability provenance-audit migrate-local migrate-dev deploy-local deploy-dev integration-stacks connectors connector-plugins benchmark recovery-check m23-validate m24-validate m25-validate clean

help:
	@echo "World Runtime developer commands"
	@echo ""
	@echo "  make install        Install dev dependencies"
	@echo "  make schemas        Validate example files against schemas"
	@echo "  make examples       Run example/scenario coherence checks"
	@echo "  make adapters       Run adapter-level checks"
	@echo "  make test           Run test suite"
	@echo "  make test-verbose   Run test suite with verbose output"
	@echo "  make evals          Run eval harness suite"
	@echo "  make air-traffic-evals  Run safety-constrained air-traffic domain tests"
	@echo "  make validate       Run schemas + tests"
	@echo "  make protocol-compat  Check App Server protocol/schema compatibility"
	@echo "  make public-api-compat  Check Public API and SDK compatibility surfaces"
	@echo "  make extension-contracts  Validate extension contract docs/templates/interfaces"
	@echo "  make scaffold-smoke  Smoke test adapter/plugin scaffold generation"
	@echo "  make ci-gate       Run CI merge gate checks"
	@echo "  make release-artifacts  Build versioned release artifacts"
	@echo "  make release-dry-run   Run CI gate then build release artifacts"
	@echo "  make fixtures       Load and summarize starter fixtures"
	@echo "  make app-client     Run App Server test client"
	@echo "  make api-server     Run Public API HTTP server"
	@echo "  make sdk-example    Run Public API Python SDK example client"
	@echo "  make workflow-quickstart  Run operator quickstart workflow"
	@echo "  make workflow-failure     Run operator failure-recovery workflow"
	@echo "  make workflow-proposal    Run operator proposal-review workflow"
	@echo "  make workflow-simulation  Run operator simulation-analysis workflow"
	@echo "  make observability    Generate telemetry diagnostics dashboard artifact"
	@echo "  make provenance-audit  Generate provenance audit export artifact"
	@echo "  make migrate-local   Apply sqlite migrations for local profile"
	@echo "  make migrate-dev     Apply sqlite migrations for dev profile"
	@echo "  make deploy-local    Run local reference deployment smoke bootstrap"
	@echo "  make deploy-dev      Run dev reference deployment smoke bootstrap"
	@echo "  make integration-stacks  Validate and smoke test integration reference stacks"
	@echo "  make connectors     Validate connector execution adapters (retries/idempotency/dead-letter)"
	@echo "  make connector-plugins  Validate transport plugins + persistent connector state + DLQ replay"
	@echo "  make benchmark      Run M23 performance benchmark harness"
	@echo "  make recovery-check Run M23 persistence recovery + migration-volume checks"
	@echo "  make m23-validate   Run M23 benchmark and recovery validation bundle"
	@echo "  make m24-validate   Run M24 extension contract + scaffold + release bundle validation"
	@echo "  make m25-validate   Run M25 v1.0 release candidate gate"
	@echo "  make clean          Remove cache files"

install:
	$(PIP) install -r requirements-dev.txt

dev: install

schemas:
	$(PYTHON) scripts/check_schemas.py

examples:
	$(PYTHON) scripts/check_examples.py

adapters:
	$(PYTHON) scripts/check_adapters.py

test:
	$(PYTHON) -m pytest -q

test-verbose:
	$(PYTHON) -m pytest -vv

evals:
	$(PYTHON) scripts/run_evals.py

air-traffic-evals:
	$(PYTHON) -m pytest -q tests/test_air_traffic_domain.py

validate: schemas test

protocol-compat:
	$(PYTHON) scripts/check_protocol_compatibility.py

public-api-compat:
	$(PYTHON) scripts/check_public_api_compatibility.py

extension-contracts:
	$(PYTHON) scripts/check_extension_contracts.py

scaffold-smoke:
	rm -rf tmp/scaffold_smoke
	$(PYTHON) scripts/scaffold_extension.py adapter --name "Scaffold Smoke Adapter" --output-dir tmp/scaffold_smoke/adapter
	$(PYTHON) scripts/scaffold_extension.py connector-plugin --name "Scaffold Smoke Connector" --provider "smoke.queue" --output-dir tmp/scaffold_smoke/connector

ci-gate: validate evals examples adapters protocol-compat public-api-compat

release-artifacts:
	$(PYTHON) scripts/build_release_artifacts.py $(if $(RELEASE_VERSION),--version $(RELEASE_VERSION),)

release-dry-run: ci-gate release-artifacts

fixtures:
	$(PYTHON) scripts/load_fixtures.py

app-client:
	$(PYTHON) cli/test_client.py

api-server:
	$(PYTHON) -m api.http_server

sdk-example:
	PYTHONPATH=. $(PYTHON) examples/clients/public_api_python_sdk_example.py

workflow-quickstart:
	$(PYTHON) scripts/run_operator_workflow.py quickstart

workflow-failure:
	$(PYTHON) scripts/run_operator_workflow.py failure-recovery

workflow-proposal:
	$(PYTHON) scripts/run_operator_workflow.py proposal-review

workflow-simulation:
	$(PYTHON) scripts/run_operator_workflow.py simulation-analysis

observability:
	$(PYTHON) scripts/run_observability_diagnostics.py

provenance-audit:
	$(PYTHON) scripts/run_observability_diagnostics.py --workflow proposal-review --include-audit-export

migrate-local:
	$(PYTHON) scripts/migrate_persistence.py --profile local

migrate-dev:
	$(PYTHON) scripts/migrate_persistence.py --profile dev

deploy-local:
	$(PYTHON) scripts/deploy_reference.py --profile local

deploy-dev:
	$(PYTHON) scripts/deploy_reference.py --profile dev

integration-stacks:
	$(PYTHON) scripts/check_integration_stacks.py

connectors:
	$(PYTHON) scripts/check_connectors.py

connector-plugins:
	$(PYTHON) scripts/check_connector_plugins.py

benchmark:
	$(PYTHON) scripts/run_performance_benchmarks.py

recovery-check:
	$(PYTHON) scripts/check_persistence_recovery.py

m23-validate: benchmark recovery-check

m24-validate: extension-contracts scaffold-smoke release-artifacts

m25-validate:
	$(PYTHON) scripts/check_release_candidate_gate.py

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
