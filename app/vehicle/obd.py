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
        self,
        vehicle: VehicleState,
        port: str | None = None,
        fast_interval: float = 0.1,
        medium_interval: float = 1.0,
        slow_interval: float = 2.0,
    ) -> None:
        super().__init__()

        self.vehicle = vehicle

        self.port = port

        # Polling intervals in seconds.
        self.fast_interval = fast_interval
        self.medium_interval = medium_interval
        self.slow_interval = slow_interval

        self.connection: obd.OBD | None = None

        self._running = False
        self._thread: threading.Thread | None = None

        self._lock = threading.Lock()

        # Track when each group was last queried.
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

        Returns True if the adapter connected successfully.
        """

        if self.connection is not None:
            if self.connection.is_connected():
                return True

        try:
            logger.info("Connecting to OBD adapter...")

            self.connection = obd.OBD(
                self.port,
                fast=False,
                timeout=2,
            )

            connected = self.connection.is_connected()

            self.vehicle.set_connected(connected)
            self.connectionChanged.emit(connected)

            if connected:
                logger.info(
                    "Connected to OBD adapter: %s",
                    self.connection.port_name(),
                )

                self._discover_supported_commands()

            else:
                logger.warning("Unable to connect to OBD adapter.")

            return connected

        except Exception as exc:
            logger.exception("Failed to connect to OBD adapter.")

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

        self._thread = threading.Thread(
            target=self._poll_loop,
            name="OBDPollingThread",
            daemon=True,
        )

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
            if self.connection is None:
                self.connect()

                # Give the adapter a moment before trying again.
                time.sleep(1.0)
                continue

            if not self.connection.is_connected():
                logger.warning("OBD connection lost.")

                self.vehicle.set_connected(False)
                self.connectionChanged.emit(False)

                self.disconnect()

                time.sleep(1.0)
                continue

            current_time = time.monotonic()

            try:
                # ------------------------------------------------------
                # Fast polling
                # ------------------------------------------------------

                if current_time - self._last_fast_poll >= self.fast_interval:
                    self._last_fast_poll = current_time

                    self._poll_fast()

                # ------------------------------------------------------
                # Medium polling
                # ------------------------------------------------------

                if current_time - self._last_medium_poll >= self.medium_interval:
                    self._last_medium_poll = current_time

                    self._poll_medium()

                # ------------------------------------------------------
                # Slow polling
                # ------------------------------------------------------

                if current_time - self._last_slow_poll >= self.slow_interval:
                    self._last_slow_poll = current_time

                    self._poll_slow()

            except Exception as exc:
                logger.exception("Error while polling OBD.")

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

            logger.info(
                "Vehicle supports %d OBD commands.",
                len(self.supported_commands),
            )

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
        # MPG ≈ MPH * 4.54 / (MAF g/s * 0.0805)
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
