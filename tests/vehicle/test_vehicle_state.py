import pytest

from app.vehicle.vehicle_state import VehicleState


def test_vehicle_state_defaults():
    vehicle = VehicleState()

    assert vehicle.rpm is None
    assert vehicle.speed is None
    assert vehicle.maf is None
    assert vehicle.mpg is None
    assert vehicle.fuelLevel is None
    assert vehicle.voltage is None
    assert vehicle.airTemperature is None
    assert vehicle.connected is False


def test_vehicle_state_updates():
    vehicle = VehicleState()

    vehicle.set_rpm(3500)
    vehicle.set_speed(65)
    vehicle.set_maf(12.5)
    vehicle.set_mpg(28.4)
    vehicle.set_fuel_level(75)
    vehicle.set_voltage(14.2)
    vehicle.set_air_temperature(72)

    assert vehicle.rpm == 3500
    assert vehicle.speed == 65
    assert vehicle.maf == 12.5
    assert vehicle.mpg == 28.4
    assert vehicle.fuelLevel == 75
    assert vehicle.voltage == 14.2
    assert vehicle.airTemperature == 72


def test_numeric_values_are_converted_to_float():
    vehicle = VehicleState()

    vehicle.set_rpm(3500)
    vehicle.set_speed(65)
    vehicle.set_maf(12)
    vehicle.set_mpg(30)
    vehicle.set_fuel_level(75)
    vehicle.set_voltage(14)
    vehicle.set_air_temperature(72)

    assert isinstance(vehicle.rpm, float)
    assert isinstance(vehicle.speed, float)
    assert isinstance(vehicle.maf, float)
    assert isinstance(vehicle.mpg, float)
    assert isinstance(vehicle.fuelLevel, float)
    assert isinstance(vehicle.voltage, float)
    assert isinstance(vehicle.airTemperature, float)


def test_measurements_can_be_set_to_none():
    vehicle = VehicleState()

    vehicle.set_rpm(3000)
    vehicle.set_speed(50)
    vehicle.set_maf(10)
    vehicle.set_mpg(25)
    vehicle.set_fuel_level(50)
    vehicle.set_voltage(14)
    vehicle.set_air_temperature(70)

    vehicle.set_rpm(None)
    vehicle.set_speed(None)
    vehicle.set_maf(None)
    vehicle.set_mpg(None)
    vehicle.set_fuel_level(None)
    vehicle.set_voltage(None)
    vehicle.set_air_temperature(None)

    assert vehicle.rpm is None
    assert vehicle.speed is None
    assert vehicle.maf is None
    assert vehicle.mpg is None
    assert vehicle.fuelLevel is None
    assert vehicle.voltage is None
    assert vehicle.airTemperature is None


def test_fuel_level_is_clamped():
    vehicle = VehicleState()

    vehicle.set_fuel_level(150)
    assert vehicle.fuelLevel == 100.0

    vehicle.set_fuel_level(-10)
    assert vehicle.fuelLevel == 0.0


def test_fuel_level_boundary_values_are_accepted():
    vehicle = VehicleState()

    vehicle.set_fuel_level(0)
    assert vehicle.fuelLevel == 0.0

    vehicle.set_fuel_level(100)
    assert vehicle.fuelLevel == 100.0


def test_connected_updates():
    vehicle = VehicleState()

    vehicle.set_connected(True)
    assert vehicle.connected is True

    vehicle.set_connected(False)
    assert vehicle.connected is False


def test_connected_is_converted_to_bool():
    vehicle = VehicleState()

    vehicle.set_connected(1)
    assert vehicle.connected is True

    vehicle.set_connected(0)
    assert vehicle.connected is False


@pytest.mark.parametrize(
    ("setter_name", "signal_name", "value"),
    [
        ("set_rpm", "rpmChanged", 3500),
        ("set_speed", "speedChanged", 65),
        ("set_maf", "mafChanged", 12.5),
        ("set_mpg", "mpgChanged", 28.4),
        ("set_fuel_level", "fuelLevelChanged", 75),
        ("set_voltage", "voltageChanged", 14.2),
        ("set_air_temperature", "airTemperatureChanged", 72),
    ],
)
def test_measurement_changed_signal_emitted(
    setter_name,
    signal_name,
    value,
):
    vehicle = VehicleState()
    changes = []

    signal = getattr(vehicle, signal_name)
    signal.connect(lambda: changes.append(True))

    setter = getattr(vehicle, setter_name)
    setter(value)

    assert changes == [True]


@pytest.mark.parametrize(
    ("setter_name", "signal_name", "value"),
    [
        ("set_rpm", "rpmChanged", 3500),
        ("set_speed", "speedChanged", 65),
        ("set_maf", "mafChanged", 12.5),
        ("set_mpg", "mpgChanged", 28.4),
        ("set_fuel_level", "fuelLevelChanged", 75),
        ("set_voltage", "voltageChanged", 14.2),
        ("set_air_temperature", "airTemperatureChanged", 72),
    ],
)
def test_measurement_changed_signal_not_emitted_when_value_is_unchanged(
    setter_name,
    signal_name,
    value,
):
    vehicle = VehicleState()
    changes = []

    signal = getattr(vehicle, signal_name)
    signal.connect(lambda: changes.append(True))

    setter = getattr(vehicle, setter_name)
    setter(value)
    setter(value)

    assert changes == [True]


def test_connected_changed_signal_emitted():
    vehicle = VehicleState()
    changes = []

    vehicle.connectedChanged.connect(lambda: changes.append(vehicle.connected))

    vehicle.set_connected(True)
    vehicle.set_connected(False)

    assert changes == [True, False]


def test_connected_changed_signal_not_emitted_when_value_is_unchanged():
    vehicle = VehicleState()
    changes = []

    vehicle.connectedChanged.connect(lambda: changes.append(vehicle.connected))

    vehicle.set_connected(False)
    vehicle.set_connected(False)

    assert changes == []


def test_reset_clears_all_values_and_disconnects():
    vehicle = VehicleState()

    vehicle.set_rpm(3500)
    vehicle.set_speed(65)
    vehicle.set_maf(12.5)
    vehicle.set_mpg(28)
    vehicle.set_fuel_level(75)
    vehicle.set_voltage(14.2)
    vehicle.set_air_temperature(72)
    vehicle.set_connected(True)

    vehicle.reset()

    assert vehicle.rpm is None
    assert vehicle.speed is None
    assert vehicle.maf is None
    assert vehicle.mpg is None
    assert vehicle.fuelLevel is None
    assert vehicle.voltage is None
    assert vehicle.airTemperature is None
    assert vehicle.connected is False


def test_clear_values_clears_measurements_but_preserves_connection():
    vehicle = VehicleState()

    vehicle.set_rpm(3500)
    vehicle.set_speed(65)
    vehicle.set_maf(12.5)
    vehicle.set_mpg(28)
    vehicle.set_fuel_level(75)
    vehicle.set_voltage(14.2)
    vehicle.set_air_temperature(72)
    vehicle.set_connected(True)

    vehicle.clear_values()

    assert vehicle.rpm is None
    assert vehicle.speed is None
    assert vehicle.maf is None
    assert vehicle.mpg is None
    assert vehicle.fuelLevel is None
    assert vehicle.voltage is None
    assert vehicle.airTemperature is None

    assert vehicle.connected is True


def test_reset_emits_change_signals():
    vehicle = VehicleState()

    vehicle.set_rpm(3500)
    vehicle.set_speed(65)
    vehicle.set_connected(True)

    changes = {
        "rpm": 0,
        "speed": 0,
        "connected": 0,
    }

    vehicle.rpmChanged.connect(lambda: changes.__setitem__("rpm", changes["rpm"] + 1))
    vehicle.speedChanged.connect(
        lambda: changes.__setitem__("speed", changes["speed"] + 1)
    )
    vehicle.connectedChanged.connect(
        lambda: changes.__setitem__("connected", changes["connected"] + 1)
    )

    vehicle.reset()

    assert changes["rpm"] == 1
    assert changes["speed"] == 1
    assert changes["connected"] == 1


def test_clear_values_emits_measurement_signals_but_not_connection_signal():
    vehicle = VehicleState()

    vehicle.set_rpm(3500)
    vehicle.set_speed(65)
    vehicle.set_connected(True)

    changes = {
        "rpm": 0,
        "speed": 0,
        "connected": 0,
    }

    vehicle.rpmChanged.connect(lambda: changes.__setitem__("rpm", changes["rpm"] + 1))
    vehicle.speedChanged.connect(
        lambda: changes.__setitem__("speed", changes["speed"] + 1)
    )
    vehicle.connectedChanged.connect(
        lambda: changes.__setitem__("connected", changes["connected"] + 1)
    )

    vehicle.clear_values()

    assert changes["rpm"] == 1
    assert changes["speed"] == 1
    assert changes["connected"] == 0


def test_repr_contains_current_state():
    vehicle = VehicleState()

    vehicle.set_rpm(3500)
    vehicle.set_speed(65)
    vehicle.set_connected(True)

    result = repr(vehicle)

    assert "VehicleState(" in result
    assert "rpm=3500.0" in result
    assert "speed=65.0" in result
    assert "connected=True" in result
