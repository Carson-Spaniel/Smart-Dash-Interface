import pytest

from app.vehicle.vehicle_state import VehicleState


@pytest.fixture
def state():
    return VehicleState()


def test_defaults(state):
    assert state.rpm == 0.0
    assert state.speed == 0.0
    assert state.maf == 0.0
    assert state.mpg == 0.0
    assert state.fuelLevel == 0.0
    assert state.voltage == 0.0
    assert state.airTemperature == 0.0
    assert state.connected is False


@pytest.mark.parametrize(
    ("setter", "getter", "value", "expected"),
    [
        ("set_rpm", "rpm", 2500, 2500.0),
        ("set_speed", "speed", 60, 60.0),
        ("set_maf", "maf", 12.5, 12.5),
        ("set_mpg", "mpg", 35, 35.0),
        ("set_fuel_level", "fuelLevel", 75, 75.0),
        ("set_voltage", "voltage", 13.8, 13.8),
        ("set_air_temperature", "airTemperature", 72, 72.0),
    ],
)
def test_setters(state, setter, getter, value, expected):
    getattr(state, setter)(value)
    assert getattr(state, getter) == expected


@pytest.mark.parametrize(("setter", "getter"), [("set_rpm", "rpm"), ("set_speed", "speed"), ("set_maf", "maf"), ("set_mpg", "mpg"), ("set_voltage", "voltage")])
def test_non_negative_values_are_clamped(state, setter, getter):
    getattr(state, setter)(-10)
    assert getattr(state, getter) == 0.0


@pytest.mark.parametrize("value, expected", [(-10, 0.0), (50, 50.0), (150, 100.0)])
def test_fuel_level_is_clamped(state, value, expected):
    state.set_fuel_level(value)
    assert state.fuelLevel == expected


def test_air_temperature_allows_negative_values(state):
    state.set_air_temperature(-20)
    assert state.airTemperature == -20.0


def test_connected_changes_and_emits_signal(state, qtbot):
    with qtbot.waitSignal(state.connectedChanged):
        state.set_connected(True)

    assert state.connected is True


def test_setting_same_value_does_not_emit(state, qtbot):
    with qtbot.assertNotEmitted(state.rpmChanged):
        state.set_rpm(0.0)


@pytest.mark.parametrize(
    ("setter", "signal"),
    [
        ("set_rpm", "rpmChanged"),
        ("set_speed", "speedChanged"),
        ("set_maf", "mafChanged"),
        ("set_mpg", "mpgChanged"),
        ("set_fuel_level", "fuelLevelChanged"),
        ("set_voltage", "voltageChanged"),
        ("set_air_temperature", "airTemperatureChanged"),
    ],
)
def test_setters_emit_signals(state, qtbot, setter, signal):
    with qtbot.waitSignal(getattr(state, signal)):
        getattr(state, setter)(1.0)


def test_clear_values_preserves_connection(state):
    state.set_rpm(1000)
    state.set_speed(40)
    state.set_connected(True)

    state.clear_values()

    assert state.rpm == 0.0
    assert state.speed == 0.0
    assert state.connected is True


def test_reset_clears_values_and_connection(state):
    state.set_rpm(1000)
    state.set_speed(40)
    state.set_fuel_level(80)
    state.set_connected(True)

    state.reset()

    assert state.rpm == 0.0
    assert state.speed == 0.0
    assert state.fuelLevel == 0.0
    assert state.connected is False


def test_repr(state):
    state.set_rpm(2500)
    state.set_speed(60)
    state.set_connected(True)

    result = repr(state)

    assert "VehicleState(" in result
    assert "rpm=2500.0" in result
    assert "speed=60.0" in result
    assert "connected=True" in result
