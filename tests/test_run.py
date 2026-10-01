from pathlib import Path
from unittest.mock import Mock

import pytest

from funstock.dataset import run


def test_cli_root_overrides_environment(monkeypatch, tmp_path):
    environment_root = tmp_path / "environment"
    cli_root = tmp_path / "cli"
    command = Mock()
    monkeypatch.setenv("FUNSTOCK_DATA_DIR", str(environment_root))
    monkeypatch.setattr(run, "run_year", command)

    run.main(["--root", str(cli_root), "year"])

    command.assert_called_once_with(cli_root)


def test_cli_requires_root_configuration(monkeypatch):
    monkeypatch.delenv("FUNSTOCK_DATA_DIR", raising=False)
    with pytest.raises(SystemExit):
        run.main(["month"])


def test_cli_uses_environment_root(monkeypatch, tmp_path):
    command = Mock()
    monkeypatch.setenv("FUNSTOCK_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(run, "run_onebyone", command)

    run.main(["onebyone"])

    command.assert_called_once_with(Path(tmp_path))
