from __future__ import annotations

import logging
import threading
import time

import obd
from obd import OBDCommand
from PySide6.QtCore import QObject, Signal

from .vehicle_state import VehicleState

logger = logging.getLogger(__name__)


class OBDVehicle(QObject):
    """
    Handles communication with an OBD-II adapter and updates VehicleState.

    OBDVehicle owns the python-obd connection and periodically polls
    supported vehicle parameters.

    VehicleState is the interface between this class and the rest of
    the application.
    """

    # Emitted when the OBD connection changes.
    connectionChanged = Signal(bool)

    # Emitted when an OBD communication error occurs.
    errorOccurred = Signal(str)

    def __init__(
        self, vehicle: VehicleState, port: str | None = None, fast_interval: float = 0.1, medium_interval: float = 1.0, slow_interval: float = 2.0
    ) -> None:
        super().__init__()

        self.vehicle = vehicle
        self.port = port

        # Polling intervals in seconds.
        self.fast_interval = fast_interval
        self.medium_interval = medium_interval
        self.slow_interval = slow_interval

        # python-obd connection.
        self.connection: obd.OBD | None = None

        # Polling thread state.
        self._running = False
        self._thread: threading.Thread | None = None

        # Protect connection access.
        self._lock = threading.Lock()

        # Track when each polling group was last queried.
        self._last_fast_poll = 0.0
        self._last_medium_poll = 0.0
        self._last_slow_poll = 0.0

        # Commands supported by the vehicle.
        self.supported_commands: set[OBDCommand] = set()

    # ==================================================================
    # Connection
    # ==================================================================

    def connect(self) -> bool:
        """
        Connect to the OBD-II adapter.

        Returns:
            True if the adapter connected successfully.
        """

        if self.connection is not None:
            try:
                if self.connection.is_connected():
                    return True
            except Exception:
                logger.exception("Unable to determine current OBD connection state.")

        try:
            logger.info("Connecting to OBD adapter...")

            connection = obd.OBD(self.port, fast=False, timeout=2)

            self.connection = connection

            connected = connection.is_connected()

            self.vehicle.set_connected(connected)
            self.connectionChanged.emit(connected)

            if connected:
                logger.info("Connected to OBD adapter: %s", connection.port_name())

                # Reset polling timers so the first successful
                # connection gets fresh data on the next polling cycle.
                now = time.monotonic()

                self._last_fast_poll = now
                self._last_medium_poll = now
                self._last_slow_poll = now

                self._discover_supported_commands()

            else:
                logger.warning("Unable to connect to OBD adapter.")

                self.supported_commands.clear()

                try:
                    connection.close()
                except Exception:
                    logger.exception("Error while closing failed OBD connection.")

                self.connection = None

            return connected

        except Exception as exc:
            logger.exception("Failed to connect to OBD adapter.")

            self.connection = None
            self.supported_commands.clear()

            self.vehicle.set_connected(False)
            self.connectionChanged.emit(False)

            self.errorOccurred.emit(str(exc))

            return False

    def disconnect(self) -> None:
        """
        Disconnect from the OBD adapter.
        """

        with self._lock:
            connection = self.connection
            self.connection = None

        self.supported_commands.clear()

        if connection is not None:
            try:
                connection.close()
            except Exception:
                logger.exception("Error while closing OBD connection.")

        self.vehicle.reset()

        self.connectionChanged.emit(False)

        logger.info("Disconnected from OBD adapter.")

    # ==================================================================
    # Polling
    # ==================================================================

    def start(self) -> None:
        """
        Start the OBD polling thread.
        """

        if self._running:
            return

        self._running = True

        self._thread = threading.Thread(target=self._poll_loop, name="OBDPollingThread", daemon=True)

        self._thread.start()

        logger.info("OBD polling started.")

    def stop(self) -> None:
        """
        Stop the OBD polling thread.
        """

        if not self._running:
            return

        logger.info("Stopping OBD polling...")

        self._running = False

        if self._thread is not None:
            self._thread.join(timeout=3)
            self._thread = None

        self.disconnect()

        logger.info("OBD polling stopped.")

    def _poll_loop(self) -> None:
        """
        Main polling loop.

        This runs outside the Qt GUI thread.
        """

        while self._running:
            # ----------------------------------------------------------
            # Connect if necessary.
            # ----------------------------------------------------------

            if self.connection is None:
                self.connect()

                if not self._running:
                    break

                # Give the adapter a moment before trying again.
                time.sleep(1.0)

                continue

            # ----------------------------------------------------------
            # Detect a lost connection.
            # ----------------------------------------------------------

            try:
                connected = self.connection.is_connected()
            except Exception:
                logger.exception("Unable to determine OBD connection state.")

                connected = False

            if not connected:
                logger.warning("OBD connection lost.")

                self.vehicle.set_connected(False)
                self.connectionChanged.emit(False)

                self.disconnect()

                if not self._running:
                    break

                time.sleep(1.0)

                continue

            # ----------------------------------------------------------
            # Poll supported commands.
            # ----------------------------------------------------------

            current_time = time.monotonic()

            # ----------------------------------------------------------
            # Fast polling
            # ----------------------------------------------------------

            if current_time - self._last_fast_poll >= self.fast_interval:
                self._last_fast_poll = current_time

                try:
                    self._poll_fast()
                except Exception as exc:
                    logger.exception("Error during fast OBD polling.")

                    self.errorOccurred.emit(str(exc))

            # ----------------------------------------------------------
            # Medium polling
            # ----------------------------------------------------------

            if current_time - self._last_medium_poll >= self.medium_interval:
                self._last_medium_poll = current_time

                try:
                    self._poll_medium()
                except Exception as exc:
                    logger.exception("Error during medium OBD polling.")

                    self.errorOccurred.emit(str(exc))

            # ----------------------------------------------------------
            # Slow polling
            # ----------------------------------------------------------

            if current_time - self._last_slow_poll >= self.slow_interval:
                self._last_slow_poll = current_time

                try:
                    self._poll_slow()
                except Exception as exc:
                    logger.exception("Error during slow OBD polling.")

                    self.errorOccurred.emit(str(exc))

            # Prevent a tight loop.
            time.sleep(0.01)

    # ==================================================================
    # Command Discovery
    # ==================================================================

    def _discover_supported_commands(self) -> None:
        """
        Determine which standard OBD commands are supported.
        """

        if self.connection is None:
            return

        try:
            supported = self.connection.supported_commands

            self.supported_commands = set(supported)

            logger.info("Vehicle supports %d OBD commands.", len(self.supported_commands))

            logger.debug("Supported OBD commands: %s", sorted(command.name for command in self.supported_commands))

        except Exception:
            logger.exception("Unable to determine supported OBD commands.")

            self.supported_commands.clear()

    def _supports(self, command: OBDCommand) -> bool:
        """
        Check whether a command is supported.
        """

        return command in self.supported_commands

    # ==================================================================
    # Fast Polling
    # ==================================================================

    def _poll_fast(self) -> None:
        """
        Poll high-frequency vehicle data.

        These values are useful for the main dashboard and should
        update frequently.
        """

        if self.connection is None:
            return

        # --------------------------------------------------------------
        # RPM
        # --------------------------------------------------------------

        if self._supports(obd.commands.RPM):
            response = self.connection.query(obd.commands.RPM)

            if not response.is_null():
                rpm = float(response.value.magnitude)

                self.vehicle.set_rpm(rpm)

        # --------------------------------------------------------------
        # Vehicle Speed
        # --------------------------------------------------------------

        if self._supports(obd.commands.SPEED):
            response = self.connection.query(obd.commands.SPEED)

            if not response.is_null():
                speed = float(response.value.to("mile/hour").magnitude)

                self.vehicle.set_speed(speed)

    # ==================================================================
    # Medium Polling
    # ==================================================================

    def _poll_medium(self) -> None:
        """
        Poll medium-frequency vehicle data.
        """

        if self.connection is None:
            return

        # --------------------------------------------------------------
        # Mass Air Flow
        # --------------------------------------------------------------

        if self._supports(obd.commands.MAF):
            response = self.connection.query(obd.commands.MAF)

            if not response.is_null():
                maf = float(response.value.to("gram / second").magnitude)

                self.vehicle.set_maf(maf)

        # --------------------------------------------------------------
        # Fuel Level
        # --------------------------------------------------------------

        if self._supports(obd.commands.FUEL_LEVEL):
            response = self.connection.query(obd.commands.FUEL_LEVEL)

            if not response.is_null():
                fuel_level = float(response.value.magnitude)

                self.vehicle.set_fuel_level(fuel_level)

        # --------------------------------------------------------------
        # Calculate MPG
        # --------------------------------------------------------------

        self._update_mpg()

    # ==================================================================
    # Slow Polling
    # ==================================================================

    def _poll_slow(self) -> None:
        """
        Poll low-frequency vehicle data.

        Diagnostic trouble codes are queried here because they are
        significantly less important to dashboard refresh rate than
        RPM and speed.
        """

        if self.connection is None:
            return

        # --------------------------------------------------------------
        # Control Module Voltage
        # --------------------------------------------------------------

        if self._supports(obd.commands.CONTROL_MODULE_VOLTAGE):
            response = self.connection.query(obd.commands.CONTROL_MODULE_VOLTAGE)

            if not response.is_null():
                voltage = float(response.value.magnitude)

                self.vehicle.set_voltage(voltage)

        # --------------------------------------------------------------
        # Ambient Air Temperature
        # --------------------------------------------------------------

        if self._supports(obd.commands.AMBIANT_AIR_TEMP):
            response = self.connection.query(obd.commands.AMBIANT_AIR_TEMP)

            if not response.is_null():
                temperature = float(response.value.magnitude)

                self.vehicle.set_air_temperature(temperature)

        # --------------------------------------------------------------
        # Diagnostic Trouble Codes
        # --------------------------------------------------------------

        self._poll_trouble_codes()

    # ==================================================================
    # Diagnostic Trouble Codes
    # ==================================================================

    def _poll_trouble_codes(self) -> None:
        """
        Poll stored and pending diagnostic trouble codes.

        Stored/confirmed codes take precedence over pending codes.

        If the vehicle reports:

            Stored:
                P0300

            Pending:
                P0300
                P0171

        VehicleState receives:

            Stored:
                P0300

            Pending:
                P0171

        This keeps the two lists mutually exclusive at the
        application level.
        """

        if self.connection is None:
            return

        stored_codes: list[dict[str, str]] = []
        pending_codes: list[dict[str, str]] = []

        # --------------------------------------------------------------
        # Stored / Confirmed DTCs - Mode 03
        # --------------------------------------------------------------

        if self._supports(obd.commands.GET_DTC):
            response = self.connection.query(obd.commands.GET_DTC)

            if not response.is_null():
                stored_codes = self._format_trouble_codes(response.value)

        # --------------------------------------------------------------
        # Pending DTCs - Mode 07
        # --------------------------------------------------------------

        if self._supports(obd.commands.GET_CURRENT_DTC):
            response = self.connection.query(obd.commands.GET_CURRENT_DTC)

            if not response.is_null():
                pending_codes = self._format_trouble_codes(response.value)

        # --------------------------------------------------------------
        # Normalize the lists.
        #
        # Stored codes always win. A code cannot appear in both
        # lists in VehicleState.
        # --------------------------------------------------------------

        stored_codes, pending_codes = self._normalize_trouble_codes(stored_codes, pending_codes)

        # --------------------------------------------------------------
        # Update VehicleState.
        # --------------------------------------------------------------

        self.vehicle.set_trouble_codes(stored_codes)

        self.vehicle.set_pending_trouble_codes(pending_codes)

        logger.debug("Stored trouble codes: %s", stored_codes)

        logger.debug("Pending trouble codes: %s", pending_codes)

    @staticmethod
    def _format_trouble_codes(codes) -> list[dict[str, str]]:
        """
        Convert python-obd DTC results into the format expected by
        VehicleState.

        python-obd normally returns:

            [
                (
                    "P0300",
                    "Random/Multiple Cylinder Misfire Detected",
                ),
                (
                    "P0420",
                    "Catalyst System Efficiency Below Threshold",
                ),
            ]

        VehicleState receives:

            [
                {
                    "code": "P0300",
                    "description": "...",
                },
            ]
        """

        formatted: list[dict[str, str]] = []

        if codes is None:
            return formatted

        for item in codes:
            try:
                code, description = item

                code = str(code).strip()

                description = str(description).strip()

                if not code:
                    continue

                formatted.append({"code": code, "description": description})

            except (TypeError, ValueError):
                logger.warning("Unable to parse OBD trouble code: %r", item)

        return formatted

    @staticmethod
    def _normalize_trouble_codes(stored_codes: list[dict[str, str]], pending_codes: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        """
        Normalize stored and pending DTC lists.

        Stored/confirmed codes always take precedence over pending
        codes.

        The returned lists are mutually exclusive.
        """

        # --------------------------------------------------------------
        # Remove duplicate stored codes.
        # --------------------------------------------------------------

        unique_stored: list[dict[str, str]] = []
        stored_code_set: set[str] = set()

        for item in stored_codes:
            code = item["code"]

            if code in stored_code_set:
                continue

            stored_code_set.add(code)

            unique_stored.append(item)

        # --------------------------------------------------------------
        # Remove duplicates from pending and remove anything that is
        # already stored.
        # --------------------------------------------------------------

        unique_pending: list[dict[str, str]] = []
        pending_code_set: set[str] = set()

        for item in pending_codes:
            code = item["code"]

            # Stored/confirmed codes take precedence.
            if code in stored_code_set:
                continue

            # Avoid duplicate pending entries.
            if code in pending_code_set:
                continue

            pending_code_set.add(code)

            unique_pending.append(item)

        return (unique_stored, unique_pending)

    # ==================================================================
    # Immediate DTC Queries
    # ==================================================================

    def query_trouble_codes(self) -> list[dict[str, str]]:
        """
        Query stored diagnostic trouble codes immediately.

        This performs a Mode 03 query and does not wait for the normal
        polling interval.

        Returns:
            A list of dictionaries containing code and description.
        """

        if self.connection is None:
            raise RuntimeError("OBD connection is not available.")

        if not self.connection.is_connected():
            raise RuntimeError("OBD connection is not connected.")

        if not self._supports(obd.commands.GET_DTC):
            logger.warning("Vehicle does not report GET_DTC as supported.")

            return []

        response = self.connection.query(obd.commands.GET_DTC)

        if response.is_null():
            return []

        trouble_codes = self._format_trouble_codes(response.value)

        # Get the current pending list so the state remains
        # mutually exclusive.
        pending_codes = self._get_pending_codes()

        trouble_codes, pending_codes = self._normalize_trouble_codes(trouble_codes, pending_codes)

        self.vehicle.set_trouble_codes(trouble_codes)

        self.vehicle.set_pending_trouble_codes(pending_codes)

        return trouble_codes

    def query_pending_trouble_codes(self) -> list[dict[str, str]]:
        """
        Query pending diagnostic trouble codes immediately.

        This performs a Mode 07 query and does not wait for the normal
        polling interval.

        Stored/confirmed codes take precedence over pending codes.

        Returns:
            A list of dictionaries containing code and description.
        """

        if self.connection is None:
            raise RuntimeError("OBD connection is not available.")

        if not self.connection.is_connected():
            raise RuntimeError("OBD connection is not connected.")

        if not self._supports(obd.commands.GET_CURRENT_DTC):
            logger.warning("Vehicle does not report GET_CURRENT_DTC as supported.")

            return []

        response = self.connection.query(obd.commands.GET_CURRENT_DTC)

        if response.is_null():
            return []

        pending_codes = self._format_trouble_codes(response.value)

        # Get the current stored list so the state remains
        # mutually exclusive.
        stored_codes = self._get_stored_codes()

        stored_codes, pending_codes = self._normalize_trouble_codes(stored_codes, pending_codes)

        self.vehicle.set_trouble_codes(stored_codes)

        self.vehicle.set_pending_trouble_codes(pending_codes)

        return pending_codes

    def _get_stored_codes(self) -> list[dict[str, str]]:
        """
        Query the vehicle for stored DTCs without changing VehicleState.

        Returns:
            A formatted list of stored DTCs.
        """

        if self.connection is None:
            return []

        if not self._supports(obd.commands.GET_DTC):
            return []

        response = self.connection.query(obd.commands.GET_DTC)

        if response.is_null():
            return []

        return self._format_trouble_codes(response.value)

    def _get_pending_codes(self) -> list[dict[str, str]]:
        """
        Query the vehicle for pending DTCs without changing VehicleState.

        Returns:
            A formatted list of pending DTCs.
        """

        if self.connection is None:
            return []

        if not self._supports(obd.commands.GET_CURRENT_DTC):
            return []

        response = self.connection.query(obd.commands.GET_CURRENT_DTC)

        if response.is_null():
            return []

        return self._format_trouble_codes(response.value)

    # ==================================================================
    # Clear Diagnostic Trouble Codes
    # ==================================================================

    def clear_trouble_codes(self) -> bool:
        """
        Clear diagnostic trouble codes from the vehicle.

        This sends the OBD Mode 04 CLEAR_DTC command.

        WARNING:
            Clearing DTCs also clears associated diagnostic data,
            such as freeze-frame information. This should only be
            called as an explicit user action.

        Returns:
            True if the clear command was accepted by the adapter.
        """

        if self.connection is None:
            raise RuntimeError("OBD connection is not available.")

        if not self.connection.is_connected():
            raise RuntimeError("OBD connection is not connected.")

        if not self._supports(obd.commands.CLEAR_DTC):
            raise RuntimeError("Vehicle does not report CLEAR_DTC as supported.")

        logger.warning("Clearing diagnostic trouble codes from vehicle.")

        response = self.connection.query(obd.commands.CLEAR_DTC)

        if response.is_null():
            logger.warning("Vehicle did not confirm DTC clear request.")

            return False

        # Clear local state immediately.
        self.vehicle.set_trouble_codes([])
        self.vehicle.set_pending_trouble_codes([])

        logger.info("Diagnostic trouble codes cleared.")

        return True

    # ==================================================================
    # MPG
    # ==================================================================

    def _update_mpg(self) -> None:
        """
        Calculate MPG from vehicle speed and MAF.

        This uses the same basic concept as the original application,
        but keeps the calculation inside the vehicle/OBD layer for now.

        A more complete implementation could move this into TripService.
        """

        speed = self.vehicle.speed
        maf = self.vehicle.maf

        if speed is None or maf is None:
            return

        if speed <= 0:
            self.vehicle.set_mpg(0.0)
            return

        if maf <= 0:
            self.vehicle.set_mpg(None)
            return

        # Approximate MPG calculation for gasoline engines.
        #
        # MPG H MPH * 4.54 / (MAF g/s * 0.0805)
        #
        # This is an estimate and depends on fuel type and assumptions.

        mpg = (speed * 4.54) / (maf * 0.0805)

        # Prevent ridiculous values caused by sensor noise.
        mpg = max(0.0, min(mpg, 200.0))

        self.vehicle.set_mpg(mpg)

    # ==================================================================
    # Manual Queries
    # ==================================================================

    def query(self, command: OBDCommand):
        """
        Execute a single OBD query.

        This is useful for commands that aren't part of the regular
        polling loop.
        """

        if self.connection is None:
            raise RuntimeError("OBD connection is not available.")

        if not self.connection.is_connected():
            raise RuntimeError("OBD connection is not connected.")

        return self.connection.query(command)
