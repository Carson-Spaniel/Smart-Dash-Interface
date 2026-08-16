import json

import pytest

from app.settings.manager import SettingsManager


@pytest.fixture
def manager(tmp_path, monkeypatch):
    path = tmp_path / "settings.json"
    monkeypatch.setattr(
        SettingsManager, "_get_settings_path", staticmethod(lambda: path)
    )
    return SettingsManager()


def test_defaults(manager):
    assert manager.rpmMin == 0
    assert manager.rpmMax == 7000
    assert manager.rpmRedline == 6500
    assert manager.rpmShift == 6000
    assert manager.shiftLightsEnabled is True
    assert manager.shiftLightPadding == 100


@pytest.mark.parametrize(
    "attr,value,expected",
    [
        ("rpmMin", -100, 0),
        ("rpmMax", -100, 0),
        ("rpmRedline", 99999, 7000),
        ("rpmShift", 99999, 7000),
        ("shiftLightColor1", -1, 0),
        ("shiftLightColor1", 999, 52),
        ("shiftLightPadding", 0, 10),
        ("shiftLightPadding", 9999, 1000),
        ("backgroundImageIndex", -1, 0),
    ],
)
def test_setters_clamp_values(manager, attr, value, expected):
    setattr(manager, attr, value)
    assert getattr(manager, attr) == expected


def test_shift_rpm_emits_rpm_and_shift_light_signals(manager, qtbot):
    with qtbot.waitSignals(
        [manager.rpmSettingsChanged, manager.shiftLightSettingsChanged],
        timeout=1000,
    ):
        manager.rpmShift = 5000


def test_shift_light_start_rpm(manager):
    manager.rpmShift = 6000
    manager.shiftLightPadding = 100

    assert manager.shiftLightStartRpm == 4600

    manager.shiftLightPadding = 1000
    assert manager.shiftLightStartRpm == manager.rpmMin


def test_save_and_load(tmp_path, monkeypatch):
    path = tmp_path / "settings.json"
    monkeypatch.setattr(
        SettingsManager, "_get_settings_path", staticmethod(lambda: path)
    )

    manager = SettingsManager()
    manager.rpmMin = 1000
    manager.rpmMax = 8000
    manager.shiftLightsEnabled = False
    manager.font1ColorIndex = 20

    loaded = SettingsManager()

    assert loaded.rpmMin == 1000
    assert loaded.rpmMax == 8000
    assert loaded.shiftLightsEnabled is False
    assert loaded.font1ColorIndex == 20


def test_invalid_json_uses_defaults(tmp_path, monkeypatch):
    path = tmp_path / "settings.json"
    path.write_text("{invalid", encoding="utf-8")
    monkeypatch.setattr(
        SettingsManager, "_get_settings_path", staticmethod(lambda: path)
    )

    manager = SettingsManager()

    assert manager.rpmMin == 0
    assert manager.rpmMax == 7000


def test_loaded_values_are_validated(tmp_path, monkeypatch):
    path = tmp_path / "settings.json"
    path.write_text(
        json.dumps(
            {
                "rpm": {"min": 5000, "max": 1000, "redline": 99999, "shift": -1},
                "shift_lights": {"color1": 999, "padding": 9999},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        SettingsManager, "_get_settings_path", staticmethod(lambda: path)
    )

    manager = SettingsManager()

    assert manager.rpmMin == 5000
    assert manager.rpmMax == 5000
    assert manager.rpmRedline == 5000
    assert manager.rpmShift == 5000
    assert manager.shiftLightColor1 == 52
    assert manager.shiftLightPadding == 1000
