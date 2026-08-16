from pathlib import Path


def test_build_script_targets_package_entrypoint():
    build = Path(__file__).parents[1] / "build_exe.py"
    text = build.read_text(encoding="utf-8")
    assert "__main__.py" in text
    assert "hiro_ust.ui" not in text
    assert "--collect-submodules=hiro_ust" in text
