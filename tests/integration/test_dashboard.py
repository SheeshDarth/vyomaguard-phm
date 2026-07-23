from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_dashboard_smoke_renders_canonical_screens():
    app_path = Path(__file__).parents[2] / "src" / "vymoa_guard_phm" / "app.py"

    app = AppTest.from_file(str(app_path)).run(timeout=15)

    assert not app.exception
    assert app.title[0].value == "VymoaGaurd PHM"
    assert [tab.label for tab in app.tabs] == [
        "Mission Overview",
        "Orbit Risk",
        "Telemetry Health",
        "Decision Report",
    ]
    assert app.selectbox[0].label == "Replay scenario"
    assert [header.value for header in app.header] == [
        "Mission Overview",
        "Orbit Risk",
        "Telemetry Health",
        "Decision Report",
    ]
    assert len(app.json) == 2
