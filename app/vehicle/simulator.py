from __future__ import annotations

import logging
import math
import random

from PySide6.QtCore import QObject, QTimer, Slot

from .vehicle_state import VehicleState

logger = logging.getLogger(__name__)


class VehicleSimulator(QObject):
    """
    Simulates vehicle data using a Qt timer.

    All VehicleState updates happen on the Qt GUI thread, which makes
    the properties safe for QML to observe.

    The simulator also provides simulated diagnostic trouble codes
    (DTCs) so the diagnostics UI can be developed and tested without
    a real vehicle.

    Diagnostic simulation:

        0-20 seconds
            No trouble codes.

        20-30 seconds
            P0300 is pending.

        30+ seconds
            P0300 becomes stored.

    A diagnostic trouble code is never present in both the stored and
    pending lists at the same time.

    Clearing the diagnostic codes resets the diagnostic simulation
    timer so the complete sequence can occur again.
    """

    def __init__(self, vehicle: VehicleState, update_interval: int = 50) -> None:
        super().__init__()

        self.vehicle = vehicle

        self._time = 0.0
        self._fuel_level = 100.0

        # --------------------------------------------------------------
        # DTC simulation state
        # --------------------------------------------------------------

        self._dtc_pending = False
        self._dtc_stored = False

        # --------------------------------------------------------------
        # Timer
        # --------------------------------------------------------------

        self._timer = QTimer(self)

        self._timer.setInterval(update_interval)

        self._timer.timeout.connect(self._update)

    # ================================================================
    # Lifecycle
    # ================================================================

    def start(self) -> None:
        """
        Start the simulator.
        """

        if self._timer.isActive():
            return

        logger.info("Starting vehicle simulator.")

        # Reset simulation state.
        self._time = 0.0
        self._fuel_level = 100.0

        self._dtc_pending = False
        self._dtc_stored = False

        self.vehicle.set_connected(True)

        self.vehicle.set_trouble_codes([])
        self.vehicle.set_pending_trouble_codes([])

        self._timer.start()

    def stop(self) -> None:
        """
        Stop the simulator.
        """

        if not self._timer.isActive():
            return

        logger.info("Stopping vehicle simulator.")

        self._timer.stop()

        self.vehicle.reset()

    # ================================================================
    # Update
    # ================================================================

    def _update(self) -> None:
        """
        Generate the next simulated vehicle state.
        """

        delta_time = self._timer.interval() / 1000.0

        self._time += delta_time

        speed = self._simulate_speed(self._time)

        rpm = self._simulate_rpm(speed, self._time)

        maf = self._simulate_maf(rpm, speed)

        mpg = self._calculate_mpg(speed, maf)

        self._update_fuel(mpg, speed, delta_time)

        voltage = self._simulate_voltage(rpm, self._time)

        air_temperature = self._simulate_air_temperature(self._time)

        # --------------------------------------------------------------
        # Vehicle measurements
        # --------------------------------------------------------------

        self.vehicle.set_rpm(rpm)
        self.vehicle.set_speed(speed)
        self.vehicle.set_maf(maf)
        self.vehicle.set_mpg(mpg)
        self.vehicle.set_fuel_level(self._fuel_level)
        self.vehicle.set_voltage(voltage)
        self.vehicle.set_air_temperature(air_temperature)

        # --------------------------------------------------------------
        # Diagnostic trouble codes
        # --------------------------------------------------------------

        self._update_dtc_state()

    # ================================================================
    # Diagnostic Trouble Codes
    # ================================================================

    @staticmethod
    def _p0300() -> dict[str, str]:
        """
        Return the simulated P0300 diagnostic trouble code.
        """

        return {"code": "P0300", "description": ("Random/Multiple Cylinder Misfire Detected")}

    def _update_dtc_state(self) -> None:
        """
        Update the simulated diagnostic trouble code state.

        State progression:

            0-20 seconds
                No codes.

            20-30 seconds
                P0300 pending.

            30+ seconds
                P0300 stored.

        A code is never present in both lists.
        """

        # --------------------------------------------------------------
        # Pending
        # --------------------------------------------------------------

        if self._time >= 20.0 and not self._dtc_pending and not self._dtc_stored:
            self._dtc_pending = True

            logger.info("Simulator: adding pending DTC P0300.")

            self.vehicle.set_pending_trouble_codes([self._p0300()])

        # --------------------------------------------------------------
        # Stored
        # --------------------------------------------------------------
        #
        # Only transition from pending -> stored.
        #
        # This prevents the simulator from creating a pending code
        # again after it has already become stored.
        #

        if self._time >= 30.0 and self._dtc_pending and not self._dtc_stored:
            self._dtc_stored = True
            self._dtc_pending = False

            logger.info("Simulator: P0300 became stored.")

            # Remove it from pending before adding it to stored.
            self.vehicle.set_pending_trouble_codes([])

            self.vehicle.set_trouble_codes([self._p0300()])

    # ================================================================
    # Clear Diagnostic Trouble Codes
    # ================================================================

    @Slot(result=bool)
    def clear_trouble_codes(self) -> bool:
        """
        Simulate clearing diagnostic trouble codes.

        In simulator mode there is no real ECU, so clearing simply
        resets the simulated diagnostic state.

        The diagnostic timer is also reset so the simulation can
        demonstrate the complete pending -> stored lifecycle again.

        Returns:
            True when the simulated clear succeeds.
        """

        logger.info("Simulator: clearing diagnostic trouble codes.")

        # --------------------------------------------------------------
        # Reset diagnostic simulation state
        # --------------------------------------------------------------

        self._dtc_pending = False
        self._dtc_stored = False

        # IMPORTANT:
        #
        # Reset only the DTC simulation clock.
        #
        # We don't reset the entire vehicle simulation because clearing
        # DTCs should not reset RPM, fuel, speed, temperature, etc.
        #

        self._time = 0.0

        # --------------------------------------------------------------
        # Clear VehicleState
        # --------------------------------------------------------------

        self.vehicle.set_trouble_codes([])

        self.vehicle.set_pending_trouble_codes([])

        logger.info("Simulator: diagnostic trouble codes cleared.")

        return True

    # ================================================================
    # Manual Diagnostic Queries
    # ================================================================

    @Slot(result="QVariantList")
    def query_trouble_codes(self) -> list[dict[str, str]]:
        """
        Return the currently simulated stored trouble codes.
        """

        return list(self.vehicle.troubleCodes)

    @Slot(result="QVariantList")
    def query_pending_trouble_codes(self) -> list[dict[str, str]]:
        """
        Return the currently simulated pending trouble codes.
        """

        return list(self.vehicle.pendingTroubleCodes)

    # ================================================================
    # Speed
    # ================================================================

    @staticmethod
    def _simulate_speed(time_value: float) -> float:
        cycle = time_value % 60.0

        if cycle < 5.0:
            speed = 0.0

        elif cycle < 15.0:
            progress = (cycle - 5.0) / 10.0

            speed = 65.0 * progress

        elif cycle < 40.0:
            speed = 65.0 + math.sin(time_value * 0.4) * 5.0

        elif cycle < 50.0:
            progress = (cycle - 40.0) / 10.0

            speed = 65.0 * (1.0 - progress)

        else:
            speed = 0.0

        if speed > 0:
            speed += random.uniform(-0.5, 0.5)

        return max(0.0, speed)

    # ================================================================
    # RPM
    # ================================================================

    @staticmethod
    def _simulate_rpm(speed: float, time_value: float) -> float:
        if speed <= 0:
            rpm = 750.0 + random.uniform(-30.0, 30.0)

        else:
            rpm = 1100.0 + speed * 35.0 + math.sin(time_value * 0.7) * 250.0

            rpm = max(900.0, min(rpm, 5000.0))

            rpm += random.uniform(-40.0, 40.0)

        return max(0.0, rpm)

    # ================================================================
    # MAF
    # ================================================================

    @staticmethod
    def _simulate_maf(rpm: float, speed: float) -> float:
        if rpm <= 0:
            return 0.0

        maf = 2.0 + (rpm / 1000.0) * 2.0 + (speed / 100.0) * 4.0

        maf += random.uniform(-0.2, 0.2)

        return max(0.1, maf)

    # ================================================================
    # MPG
    # ================================================================

    @staticmethod
    def _calculate_mpg(speed: float, maf: float) -> float:
        if speed <= 0 or maf <= 0:
            return 0.0

        mpg = (speed * 4.53592) / (maf * 0.0617)

        return max(0.0, min(mpg, 200.0))

    # ================================================================
    # Fuel
    # ================================================================

    def _update_fuel(self, mpg: float, speed: float, delta_time: float) -> None:
        if speed <= 0 or mpg <= 0:
            return

        # Simulated fuel consumption.
        self._fuel_level -= 0.05

        self._fuel_level = max(0.0, min(100.0, self._fuel_level))

    # ================================================================
    # Voltage
    # ================================================================

    @staticmethod
    def _simulate_voltage(rpm: float, time_value: float) -> float:
        if rpm < 500:
            voltage = 12.4

        else:
            voltage = 14.2 + math.sin(time_value * 0.3) * 0.15

        voltage += random.uniform(-0.03, 0.03)

        return max(0.0, voltage)

    # ================================================================
    # Air Temperature
    # ================================================================

    @staticmethod
    def _simulate_air_temperature(time_value: float) -> float:
        temperature = 72.0 + math.sin(time_value / 30.0) * 2.0 + random.uniform(-0.1, 0.1)

        return temperature
