from unittest.mock import MagicMock, patch

import pytest

from app.vehicle.obd import OBDVehicle
from app.vehicle.vehicle_state import VehicleState

# ======================================================================
# Fixtures / Helpers
# ======================================================================


@pytest.fixture
def vehicle_state():
    return VehicleState()


@pytest.fixture
def obd_vehicle(vehicle_state):
    return OBDVehicle(vehicle_state)


def make_response(value, converted_value=None):
    response = MagicMock()
    response.is_null.return_value = False

    response.value.magnitude = value

    if converted_value is None:
        converted_value = value

    response.value.to.return_value.magnitude = converted_value

    return response


# ======================================================================
# Initialization
# ======================================================================


def test_obd_vehicle_defaults(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    assert vehicle.vehicle is vehicle_state
    assert vehicle.port is None

    assert vehicle.connection is None
    assert vehicle._running is False
    assert vehicle._thread is None

    assert vehicle.fast_interval == 0.1
    assert vehicle.medium_interval == 1.0
    assert vehicle.slow_interval == 2.0

    assert vehicle.supported_commands == set()


def test_obd_vehicle_accepts_custom_configuration(vehicle_state):
    vehicle = OBDVehicle(
        vehicle_state,
        port="/dev/ttyUSB0",
        fast_interval=0.2,
        medium_interval=2.0,
        slow_interval=5.0,
    )

    assert vehicle.port == "/dev/ttyUSB0"
    assert vehicle.fast_interval == 0.2
    assert vehicle.medium_interval == 2.0
    assert vehicle.slow_interval == 5.0


# ======================================================================
# Connection
# ======================================================================


@patch("app.vehicle.obd.obd.OBD")
def test_connect_success(mock_obd, vehicle_state):
    connection = MagicMock()

    connection.is_connected.return_value = True
    connection.port_name.return_value = "/dev/ttyUSB0"
    connection.supported_commands = set()

    mock_obd.return_value = connection

    vehicle = OBDVehicle(vehicle_state)

    result = vehicle.connect()

    assert result is True
    assert vehicle.connection is connection
    assert vehicle_state.connected is True

    mock_obd.assert_called_once_with(
        None,
        fast=False,
        timeout=2,
    )


@patch("app.vehicle.obd.obd.OBD")
def test_connect_passes_port_to_obd(mock_obd, vehicle_state):
    connection = MagicMock()

    connection.is_connected.return_value = True
    connection.port_name.return_value = "/dev/ttyUSB0"
    connection.supported_commands = set()

    mock_obd.return_value = connection

    vehicle = OBDVehicle(
        vehicle_state,
        port="/dev/ttyUSB0",
    )

    result = vehicle.connect()

    assert result is True

    mock_obd.assert_called_once_with(
        "/dev/ttyUSB0",
        fast=False,
        timeout=2,
    )


@patch("app.vehicle.obd.obd.OBD")
def test_connect_discovers_supported_commands(mock_obd, vehicle_state):
    connection = MagicMock()

    connection.is_connected.return_value = True
    connection.port_name.return_value = "/dev/ttyUSB0"

    supported_commands = {
        "RPM",
        "SPEED",
    }

    connection.supported_commands = supported_commands

    mock_obd.return_value = connection

    vehicle = OBDVehicle(vehicle_state)

    vehicle.connect()

    assert vehicle.supported_commands == supported_commands


@patch("app.vehicle.obd.obd.OBD")
def test_connect_failure_returns_false(mock_obd, vehicle_state):
    mock_obd.side_effect = RuntimeError("adapter unavailable")

    vehicle = OBDVehicle(vehicle_state)
    errors = []

    vehicle.errorOccurred.connect(errors.append)

    result = vehicle.connect()

    assert result is False
    assert vehicle.connection is None
    assert vehicle_state.connected is False
    assert errors == ["adapter unavailable"]


@patch("app.vehicle.obd.obd.OBD")
def test_connect_failure_emits_connection_changed_false(
    mock_obd,
    vehicle_state,
):
    mock_obd.side_effect = RuntimeError("adapter unavailable")

    vehicle = OBDVehicle(vehicle_state)
    changes = []

    vehicle.connectionChanged.connect(changes.append)

    vehicle.connect()

    assert changes == [False]


@patch("app.vehicle.obd.obd.OBD")
def test_connect_returns_true_if_already_connected(
    mock_obd,
    vehicle_state,
):
    connection = MagicMock()
    connection.is_connected.return_value = True

    vehicle = OBDVehicle(vehicle_state)
    vehicle.connection = connection

    result = vehicle.connect()

    assert result is True
    assert vehicle.connection is connection

    mock_obd.assert_not_called()


@patch("app.vehicle.obd.obd.OBD")
def test_connect_handles_adapter_that_is_not_connected(
    mock_obd,
    vehicle_state,
):
    connection = MagicMock()

    connection.is_connected.return_value = False

    mock_obd.return_value = connection

    vehicle = OBDVehicle(vehicle_state)
    changes = []

    vehicle.connectionChanged.connect(changes.append)

    result = vehicle.connect()

    assert result is False
    assert vehicle.connection is connection
    assert vehicle_state.connected is False
    assert changes == [False]


# ======================================================================
# Disconnect
# ======================================================================


def test_disconnect_closes_connection(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    connection = MagicMock()

    vehicle.connection = connection
    vehicle_state.set_connected(True)

    changes = []
    vehicle.connectionChanged.connect(changes.append)

    vehicle.disconnect()

    connection.close.assert_called_once()

    assert vehicle.connection is None
    assert vehicle_state.connected is False
    assert changes == [False]


def test_disconnect_without_connection_is_safe(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    vehicle.disconnect()

    assert vehicle.connection is None
    assert vehicle_state.connected is False


def test_disconnect_handles_close_error(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    connection = MagicMock()
    connection.close.side_effect = RuntimeError("close failed")

    vehicle.connection = connection
    vehicle_state.set_connected(True)

    vehicle.disconnect()

    assert vehicle.connection is None
    assert vehicle_state.connected is False


# ======================================================================
# Supported Commands
# ======================================================================


def test_supports_returns_true_for_supported_command(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    command = MagicMock()

    vehicle.supported_commands = {command}

    assert vehicle._supports(command) is True


def test_supports_returns_false_for_unsupported_command(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    command = MagicMock()

    vehicle.supported_commands = set()

    assert vehicle._supports(command) is False


def test_discover_supported_commands_without_connection(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    vehicle._discover_supported_commands()

    assert vehicle.supported_commands == set()


def test_discover_supported_commands(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    command_one = MagicMock()
    command_two = MagicMock()

    connection = MagicMock()
    connection.supported_commands = {
        command_one,
        command_two,
    }

    vehicle.connection = connection

    vehicle._discover_supported_commands()

    assert vehicle.supported_commands == {
        command_one,
        command_two,
    }


def test_discover_supported_commands_failure_clears_commands(
    vehicle_state,
):
    vehicle = OBDVehicle(vehicle_state)

    vehicle.supported_commands = {"existing"}

    connection = MagicMock()

    type(connection).supported_commands = property(
        lambda _: (_ for _ in ()).throw(RuntimeError("discovery failed"))
    )

    vehicle.connection = connection

    vehicle._discover_supported_commands()

    assert vehicle.supported_commands == set()


# ======================================================================
# Fast Polling
# ======================================================================


def test_poll_fast_without_connection_does_nothing(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    vehicle._poll_fast()

    assert vehicle_state.rpm is None
    assert vehicle_state.speed is None


def test_poll_fast_updates_rpm(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    connection = MagicMock()
    vehicle.connection = connection

    rpm_command = MagicMock()
    response = make_response(3500)

    connection.query.return_value = response
    vehicle.supported_commands = {rpm_command}

    with patch(
        "app.vehicle.obd.obd.commands.RPM",
        rpm_command,
    ):
        vehicle._poll_fast()

    assert vehicle_state.rpm == 3500.0
    connection.query.assert_called_once_with(rpm_command)


def test_poll_fast_updates_speed(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    connection = MagicMock()
    vehicle.connection = connection

    speed_command = MagicMock()
    response = make_response(
        65,
        converted_value=65,
    )

    connection.query.return_value = response
    vehicle.supported_commands = {speed_command}

    with patch(
        "app.vehicle.obd.obd.commands.SPEED",
        speed_command,
    ):
        vehicle._poll_fast()

    assert vehicle_state.speed == 65.0


def test_poll_fast_converts_speed_to_mph(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    connection = MagicMock()
    vehicle.connection = connection

    speed_command = MagicMock()
    response = make_response(
        104.607,
        converted_value=65,
    )

    connection.query.return_value = response
    vehicle.supported_commands = {speed_command}

    with patch(
        "app.vehicle.obd.obd.commands.SPEED",
        speed_command,
    ):
        vehicle._poll_fast()

    response.value.to.assert_called_once_with("mile/hour")
    assert vehicle_state.speed == 65.0


def test_poll_fast_ignores_null_rpm_response(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    connection = MagicMock()
    vehicle.connection = connection

    rpm_command = MagicMock()

    response = MagicMock()
    response.is_null.return_value = True

    connection.query.return_value = response
    vehicle.supported_commands = {rpm_command}

    with patch(
        "app.vehicle.obd.obd.commands.RPM",
        rpm_command,
    ):
        vehicle._poll_fast()

    assert vehicle_state.rpm is None


def test_poll_fast_ignores_null_speed_response(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    connection = MagicMock()
    vehicle.connection = connection

    speed_command = MagicMock()

    response = MagicMock()
    response.is_null.return_value = True

    connection.query.return_value = response
    vehicle.supported_commands = {speed_command}

    with patch(
        "app.vehicle.obd.obd.commands.SPEED",
        speed_command,
    ):
        vehicle._poll_fast()

    assert vehicle_state.speed is None


def test_poll_fast_does_not_query_unsupported_commands(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    connection = MagicMock()
    vehicle.connection = connection
    vehicle.supported_commands = set()

    vehicle._poll_fast()

    connection.query.assert_not_called()


# ======================================================================
# Medium Polling
# ======================================================================


def test_poll_medium_without_connection_does_nothing(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    vehicle._poll_medium()

    assert vehicle_state.maf is None
    assert vehicle_state.fuelLevel is None


def test_poll_medium_updates_maf(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    connection = MagicMock()
    vehicle.connection = connection

    maf_command = MagicMock()
    response = make_response(
        12.5,
        converted_value=12.5,
    )

    connection.query.return_value = response
    vehicle.supported_commands = {maf_command}

    with patch(
        "app.vehicle.obd.obd.commands.MAF",
        maf_command,
    ):
        vehicle._poll_medium()

    response.value.to.assert_called_once_with("gram / second")
    assert vehicle_state.maf == 12.5


def test_poll_medium_updates_fuel_level(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    connection = MagicMock()
    vehicle.connection = connection

    fuel_command = MagicMock()
    response = make_response(75)

    connection.query.return_value = response
    vehicle.supported_commands = {fuel_command}

    with patch(
        "app.vehicle.obd.obd.commands.FUEL_LEVEL",
        fuel_command,
    ):
        vehicle._poll_medium()

    assert vehicle_state.fuelLevel == 75.0


def test_poll_medium_ignores_null_maf_response(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    connection = MagicMock()
    vehicle.connection = connection

    maf_command = MagicMock()

    response = MagicMock()
    response.is_null.return_value = True

    connection.query.return_value = response
    vehicle.supported_commands = {maf_command}

    with patch(
        "app.vehicle.obd.obd.commands.MAF",
        maf_command,
    ):
        vehicle._poll_medium()

    assert vehicle_state.maf is None


def test_poll_medium_ignores_null_fuel_response(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    connection = MagicMock()
    vehicle.connection = connection

    fuel_command = MagicMock()

    response = MagicMock()
    response.is_null.return_value = True

    connection.query.return_value = response
    vehicle.supported_commands = {fuel_command}

    with patch(
        "app.vehicle.obd.obd.commands.FUEL_LEVEL",
        fuel_command,
    ):
        vehicle._poll_medium()

    assert vehicle_state.fuelLevel is None


def test_poll_medium_updates_mpg(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    vehicle.connection = MagicMock()

    vehicle_state.set_speed(60)
    vehicle_state.set_maf(10)

    with patch.object(vehicle, "_update_mpg") as update_mpg:
        vehicle._poll_medium()

    update_mpg.assert_called_once()


# ======================================================================
# Slow Polling
# ======================================================================


def test_poll_slow_without_connection_does_nothing(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    vehicle._poll_slow()

    assert vehicle_state.voltage is None
    assert vehicle_state.airTemperature is None


def test_poll_slow_updates_voltage(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    connection = MagicMock()
    vehicle.connection = connection

    voltage_command = MagicMock()
    response = make_response(14.2)

    connection.query.return_value = response
    vehicle.supported_commands = {voltage_command}

    with patch(
        "app.vehicle.obd.obd.commands.CONTROL_MODULE_VOLTAGE",
        voltage_command,
    ):
        vehicle._poll_slow()

    assert vehicle_state.voltage == 14.2


def test_poll_slow_updates_air_temperature(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    connection = MagicMock()
    vehicle.connection = connection

    temperature_command = MagicMock()
    response = make_response(72)

    connection.query.return_value = response
    vehicle.supported_commands = {temperature_command}

    with patch(
        "app.vehicle.obd.obd.commands.AMBIANT_AIR_TEMP",
        temperature_command,
    ):
        vehicle._poll_slow()

    assert vehicle_state.airTemperature == 72.0


def test_poll_slow_ignores_null_voltage_response(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    connection = MagicMock()
    vehicle.connection = connection

    voltage_command = MagicMock()

    response = MagicMock()
    response.is_null.return_value = True

    connection.query.return_value = response
    vehicle.supported_commands = {voltage_command}

    with patch(
        "app.vehicle.obd.obd.commands.CONTROL_MODULE_VOLTAGE",
        voltage_command,
    ):
        vehicle._poll_slow()

    assert vehicle_state.voltage is None


def test_poll_slow_ignores_null_temperature_response(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    connection = MagicMock()
    vehicle.connection = connection

    temperature_command = MagicMock()

    response = MagicMock()
    response.is_null.return_value = True

    connection.query.return_value = response
    vehicle.supported_commands = {temperature_command}

    with patch(
        "app.vehicle.obd.obd.commands.AMBIANT_AIR_TEMP",
        temperature_command,
    ):
        vehicle._poll_slow()

    assert vehicle_state.airTemperature is None


# ======================================================================
# MPG
# ======================================================================


def test_update_mpg_does_nothing_without_speed(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    vehicle_state.set_maf(10)

    vehicle._update_mpg()

    assert vehicle_state.mpg is None


def test_update_mpg_does_nothing_without_maf(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    vehicle_state.set_speed(60)

    vehicle._update_mpg()

    assert vehicle_state.mpg is None


def test_update_mpg_returns_zero_when_speed_is_zero(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    vehicle_state.set_speed(0)
    vehicle_state.set_maf(10)

    vehicle._update_mpg()

    assert vehicle_state.mpg == 0.0


def test_update_mpg_clears_mpg_when_maf_is_zero(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    vehicle_state.set_speed(60)
    vehicle_state.set_maf(0)
    vehicle_state.set_mpg(25)

    vehicle._update_mpg()

    assert vehicle_state.mpg is None


def test_update_mpg_clears_mpg_when_maf_is_negative(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    vehicle_state.set_speed(60)
    vehicle_state.set_maf(-1)
    vehicle_state.set_mpg(25)

    vehicle._update_mpg()

    assert vehicle_state.mpg is None


def test_update_mpg_calculates_expected_value(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    vehicle_state.set_speed(30)
    vehicle_state.set_maf(10)

    vehicle._update_mpg()

    expected = (30 * 4.54) / (10 * 0.0805)

    assert vehicle_state.mpg == pytest.approx(expected)


def test_update_mpg_is_capped_at_200(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    vehicle_state.set_speed(200)
    vehicle_state.set_maf(0.01)

    vehicle._update_mpg()

    assert vehicle_state.mpg == 200.0


def test_update_mpg_never_goes_below_zero(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    vehicle_state.set_speed(60)
    vehicle_state.set_maf(10)

    vehicle._update_mpg()

    assert vehicle_state.mpg >= 0.0


# ======================================================================
# Manual Queries
# ======================================================================


def test_query_requires_connection(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    with pytest.raises(
        RuntimeError,
        match="OBD connection is not available",
    ):
        vehicle.query(MagicMock())


def test_query_requires_connected_adapter(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    connection = MagicMock()
    connection.is_connected.return_value = False

    vehicle.connection = connection

    with pytest.raises(
        RuntimeError,
        match="OBD connection is not connected",
    ):
        vehicle.query(MagicMock())

    connection.query.assert_not_called()


def test_query_returns_obd_response(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    connection = MagicMock()
    connection.is_connected.return_value = True

    expected_response = MagicMock()

    connection.query.return_value = expected_response

    vehicle.connection = connection

    command = MagicMock()

    result = vehicle.query(command)

    assert result is expected_response
    connection.query.assert_called_once_with(command)


# ======================================================================
# Start / Stop
# ======================================================================


def test_start_sets_running_and_creates_thread(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    with patch("app.vehicle.obd.threading.Thread") as mock_thread:
        thread = mock_thread.return_value

        vehicle.start()

        assert vehicle._running is True
        assert vehicle._thread is thread

        mock_thread.assert_called_once_with(
            target=vehicle._poll_loop,
            name="OBDPollingThread",
            daemon=True,
        )

        thread.start.assert_called_once()


def test_start_does_nothing_if_already_running(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    vehicle._running = True

    with patch("app.vehicle.obd.threading.Thread") as mock_thread:
        vehicle.start()

    mock_thread.assert_not_called()


def test_stop_does_nothing_if_not_running(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    with patch.object(vehicle, "disconnect") as disconnect:
        vehicle.stop()

    disconnect.assert_not_called()


def test_stop_stops_thread_and_disconnects(vehicle_state):
    vehicle = OBDVehicle(vehicle_state)

    thread = MagicMock()

    vehicle._running = True
    vehicle._thread = thread

    with patch.object(vehicle, "disconnect") as disconnect:
        vehicle.stop()

    assert vehicle._running is False
    assert vehicle._thread is None

    thread.join.assert_called_once_with(timeout=3)
    disconnect.assert_called_once()
