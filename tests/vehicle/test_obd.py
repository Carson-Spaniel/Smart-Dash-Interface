from unittest.mock import MagicMock, patch

import obd
import pytest

from app.vehicle.obd import OBDVehicle


@pytest.fixture
def vehicle():
    vehicle = MagicMock()
    vehicle.speed = None
    vehicle.maf = None
    return vehicle


@pytest.fixture
def sut(vehicle):
    return OBDVehicle(vehicle)


def test_connect_success(sut, vehicle):
    connection = MagicMock()
    connection.is_connected.return_value = True
    connection.supported_commands = {obd.commands.RPM}

    with patch("app.vehicle.obd.obd.OBD", return_value=connection):
        assert sut.connect() is True

    assert sut.connection is connection
    vehicle.set_connected.assert_called_once_with(True)
    assert sut.supported_commands == {obd.commands.RPM}


def test_connect_failure(sut, vehicle):
    with patch("app.vehicle.obd.obd.OBD", side_effect=Exception("boom")):
        assert sut.connect() is False

    vehicle.set_connected.assert_called_once_with(False)


def test_connect_reuses_existing_connection(sut):
    sut.connection = MagicMock()
    sut.connection.is_connected.return_value = True

    with patch("app.vehicle.obd.obd.OBD") as obd_cls:
        assert sut.connect() is True

    obd_cls.assert_not_called()


def test_disconnect(sut, vehicle):
    connection = MagicMock()
    sut.connection = connection

    sut.disconnect()

    connection.close.assert_called_once()
    vehicle.reset.assert_called_once()
    assert sut.connection is None


def test_discover_supported_commands(sut):
    sut.connection = MagicMock()
    sut.connection.supported_commands = {
        obd.commands.RPM,
        obd.commands.SPEED,
    }

    sut._discover_supported_commands()

    assert sut.supported_commands == {
        obd.commands.RPM,
        obd.commands.SPEED,
    }


def test_poll_fast(sut, vehicle):
    sut.connection = MagicMock()
    sut.supported_commands = {
        obd.commands.RPM,
        obd.commands.SPEED,
    }

    rpm = MagicMock()
    rpm.is_null.return_value = False
    rpm.value.magnitude = 2500

    speed = MagicMock()
    speed.is_null.return_value = False
    speed.value.to.return_value.magnitude = 55

    sut.connection.query.side_effect = [rpm, speed]

    sut._poll_fast()

    vehicle.set_rpm.assert_called_once_with(2500.0)
    vehicle.set_speed.assert_called_once_with(55.0)


def test_poll_medium(sut, vehicle):
    sut.connection = MagicMock()
    sut.supported_commands = {
        obd.commands.MAF,
        obd.commands.FUEL_LEVEL,
    }

    maf = MagicMock()
    maf.is_null.return_value = False
    maf.value.to.return_value.magnitude = 12.5

    fuel = MagicMock()
    fuel.is_null.return_value = False
    fuel.value.magnitude = 72

    sut.connection.query.side_effect = [maf, fuel]
    sut._update_mpg = MagicMock()

    sut._poll_medium()

    vehicle.set_maf.assert_called_once_with(12.5)
    vehicle.set_fuel_level.assert_called_once_with(72.0)
    sut._update_mpg.assert_called_once()


def test_poll_slow(sut, vehicle):
    sut.connection = MagicMock()
    sut.supported_commands = {
        obd.commands.CONTROL_MODULE_VOLTAGE,
        obd.commands.AMBIANT_AIR_TEMP,
    }

    voltage = MagicMock()
    voltage.is_null.return_value = False
    voltage.value.magnitude = 13.8

    temperature = MagicMock()
    temperature.is_null.return_value = False
    temperature.value.magnitude = 25

    sut.connection.query.side_effect = [voltage, temperature]

    sut._poll_slow()

    vehicle.set_voltage.assert_called_once_with(13.8)
    vehicle.set_air_temperature.assert_called_once_with(25.0)


@pytest.mark.parametrize(
    ("speed", "maf", "expected"),
    [
        (60, 10, 200.0),
        (0, 10, 0.0),
        (60, 0, None),
        (None, 10, None),
        (60, None, None),
    ],
)
def test_update_mpg(sut, vehicle, speed, maf, expected):
    vehicle.speed = speed
    vehicle.maf = maf

    sut._update_mpg()

    if speed is None or maf is None:
        vehicle.set_mpg.assert_not_called()
    else:
        vehicle.set_mpg.assert_called_once_with(expected)


def test_update_mpg_clamps_to_200(sut, vehicle):
    vehicle.speed = 200
    vehicle.maf = 0.01

    sut._update_mpg()

    vehicle.set_mpg.assert_called_once_with(200.0)


def test_query_requires_connection(sut):
    with pytest.raises(RuntimeError, match="not available"):
        sut.query(obd.commands.RPM)


def test_query_requires_connected_adapter(sut):
    sut.connection = MagicMock()
    sut.connection.is_connected.return_value = False

    with pytest.raises(RuntimeError, match="not connected"):
        sut.query(obd.commands.RPM)


def test_query(sut):
    sut.connection = MagicMock()
    sut.connection.is_connected.return_value = True

    response = MagicMock()
    sut.connection.query.return_value = response

    assert sut.query(obd.commands.RPM) is response
    sut.connection.query.assert_called_once_with(obd.commands.RPM)


def test_start_is_idempotent(sut):
    with patch("app.vehicle.obd.threading.Thread") as thread_cls:
        sut.start()
        sut.start()

    thread_cls.assert_called_once()
    thread_cls.return_value.start.assert_called_once()


def test_stop(sut):
    sut._running = True
    sut._thread = MagicMock()
    sut.disconnect = MagicMock()

    sut.stop()

    assert sut._running is False
    assert sut._thread is None
    sut.disconnect.assert_called_once()
