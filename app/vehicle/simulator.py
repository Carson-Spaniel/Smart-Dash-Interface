from __future__ import annotations

import logging
import math
import random

from PySide6.QtCore import QObject, QTimer

from .vehicle_state import VehicleState

logger = logging.getLogger(__name__)


class VehicleSimulator(QObject):
    """
    Simulates vehicle data using a Qt timer.

    All VehicleState updates happen on the Qt GUI thread, which makes
    the properties safe for QML to observe.
    """

    def __init__(
        self,
        vehicle: VehicleState,
        update_interval: int = 50,
    ) -> None:
        super().__init__()

        self.vehicle = vehicle

        self._time = 0.0
        self._fuel_level = 100.0

        self._timer = QTimer(self)

        self._timer.setInterval(update_interval)

        self._timer.timeout.connect(self._update)

    # ================================================================
    # Lifecycle
    # ================================================================

    def start(self) -> None:
        """Start the simulator."""

        if self._timer.isActive():
            return

        logger.info("Starting vehicle simulator.")

        self.vehicle.set_connected(True)

        self._timer.start()

    def stop(self) -> None:
        """Stop the simulator."""

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

        # 50 ms = 0.05 seconds.
        delta_time = self._timer.interval() / 1000.0

        self._time += delta_time

        speed = self._simulate_speed(self._time)

        rpm = self._simulate_rpm(
            speed,
            self._time,
        )

        maf = self._simulate_maf(
            rpm,
            speed,
        )

        mpg = self._calculate_mpg(
            speed,
            maf,
        )

        self._update_fuel(
            mpg,
            speed,
            delta_time,
        )

        voltage = self._simulate_voltage(
            rpm,
            self._time,
        )

        air_temperature = self._simulate_air_temperature(
            self._time,
        )

        self.vehicle.set_rpm(rpm)
        self.vehicle.set_speed(speed)
        self.vehicle.set_maf(maf)
        self.vehicle.set_mpg(mpg)
        self.vehicle.set_fuel_level(self._fuel_level)
        self.vehicle.set_voltage(voltage)
        self.vehicle.set_air_temperature(air_temperature)

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
    def _simulate_rpm(
        speed: float,
        time_value: float,
    ) -> float:
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
    def _simulate_maf(
        rpm: float,
        speed: float,
    ) -> float:
        if rpm <= 0:
            return 0.0

        maf = 2.0 + (rpm / 1000.0) * 2.0 + (speed / 100.0) * 4.0

        maf += random.uniform(-0.2, 0.2)

        return max(0.1, maf)

    # ================================================================
    # MPG
    # ================================================================

    @staticmethod
    def _calculate_mpg(
        speed: float,
        maf: float,
    ) -> float:
        if speed <= 0 or maf <= 0:
            return 0.0

        mpg = (speed * 4.53592) / (maf * 0.0617)

        return max(
            0.0,
            min(mpg, 200.0),
        )

    # ================================================================
    # Fuel
    # ================================================================

    def _update_fuel(
        self,
        mpg: float,
        speed: float,
        delta_time: float,
    ) -> None:
        if speed <= 0 or mpg <= 0:
            return

        # fuel_consumed = speed / mpg * delta_time / 3600.0 * 20.0

        # self._fuel_level -= fuel_consumed
        self._fuel_level -= 0.05

        self._fuel_level = max(
            0.0,
            min(100.0, self._fuel_level),
        )

    # ================================================================
    # Voltage
    # ================================================================

    @staticmethod
    def _simulate_voltage(
        rpm: float,
        time_value: float,
    ) -> float:
        if rpm < 500:
            voltage = 12.4
        else:
            voltage = 14.2 + math.sin(time_value * 0.3) * 0.15

        voltage += random.uniform(
            -0.03,
            0.03,
        )

        return max(0.0, voltage)

    # ================================================================
    # Air Temperature
    # ================================================================

    @staticmethod
    def _simulate_air_temperature(
        time_value: float,
    ) -> float:
        temperature = (
            72.0 + math.sin(time_value / 30.0) * 2.0 + random.uniform(-0.1, 0.1)
        )

        return temperature
