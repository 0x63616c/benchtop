import json

from splitflap_cad.__main__ import main


def test_list_json(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["splitflap_cad", "list", "--json"])
    main()
    data = json.loads(capsys.readouterr().out)
    assert data["projects"]["split-flap"] == "modular split-flap display"
    assert "assembly" in data["models"]
    assert data["model_projects"]["assembly"] == "split-flap"
    assert data["model_projects"]["blinds-unit"] == "blinds"
    assert data["printable_projects"]["blinds-frame"] == "blinds"
    assert data["render_projects"]["mirror-light-layout"] == "mirror-light"
    assert set(data["printable"]) <= set(data["models"]) | set(data["printable"])
    assert all(isinstance(v, str) for v in data["src_to_model"].values())


def test_list_human_groups_models_by_project(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["splitflap_cad", "list"])
    main()
    output = capsys.readouterr().out
    assert "projects:" in output
    assert "  split-flap — modular split-flap display" in output
    assert "  blinds — motorized roller-blind drive" in output
    assert output.index("  split-flap —") < output.index("      assembly")
    assert output.index("  blinds —") < output.index("      blinds-unit")
