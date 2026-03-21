from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_app_server_no_longer_imports_core_world_game_module():
    source = (REPO_ROOT / "core" / "app_server.py").read_text(encoding="utf-8")

    assert "from core.domains.world_game import" not in source
    assert "self.world_game_service" in source
