# app/vehicle/vehicle_state.py

from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal


class VehicleState(QObject):
    """
    Represents the current state of the vehicle.

    VehicleState is intentionally independent of the OBD implementation.
    It does not communicate with the vehicle or perform OBD queries.

    Vehicle backends update this object, and QML observes its properties
    through Qt signals.

    Units:
        rpm:                RPM
        speed:              MPH
        maf:                grams / second
        mpg:                miles / gallon
        fuelLevel:          percent (0-100)
        voltage:            volts
        airTemperature:     degrees Fahrenheit
    """

    # ------------------------------------------------------------------
    # Signals
    # ------------------------------------------------------------------

    rpmChanged = Signal()
    speedChanged = Signal()
    mafChanged = Signal()
    mpgChanged = Signal()
    fuelLevelChanged = Signal()
    voltageChanged = Signal()
    airTemperatureChanged = Signal()
    connectedChanged = Signal()

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        super().__init__()

        self._rpm = 0.0
        self._speed = 0.0
        self._maf = 0.0
        self._mpg = 0.0
        self._fuel_level = 0.0
        self._voltage = 0.0
        self._air_temperature = 0.0

        self._connected = False

    # ==================================================================
    # RPM
    # ==================================================================

    def get_rpm(self) -> float:
        return self._rpm

    def set_rpm(self, value: float) -> None:
        value = max(0.0, float(value))

        if self._rpm == value:
            return

        self._rpm = value
        self.rpmChanged.emit()

    rpm = Property(
        float,
        get_rpm,
        set_rpm,
        notify=rpmChanged,
    )

    # ==================================================================
    # Speed
    # ==================================================================

    def get_speed(self) -> float:
        return self._speed

    def set_speed(self, value: float) -> None:
        value = max(0.0, float(value))

        if self._speed == value:
            return

        self._speed = value
        self.speedChanged.emit()

    speed = Property(
        float,
        get_speed,
        set_speed,
        notify=speedChanged,
    )

    # ==================================================================
    # Mass Air Flow
    # ==================================================================

    def get_maf(self) -> float:
        return self._maf

    def set_maf(self, value: float) -> None:
        value = max(0.0, float(value))

        if self._maf == value:
            return

        self._maf = value
        self.mafChanged.emit()

    maf = Property(
        float,
        get_maf,
        set_maf,
        notify=mafChanged,
    )

    # ==================================================================
    # Miles Per Gallon
    # ==================================================================

    def get_mpg(self) -> float:
        return self._mpg

    def set_mpg(self, value: float) -> None:
        value = max(0.0, float(value))

        if self._mpg == value:
            return

        self._mpg = value
        self.mpgChanged.emit()

    mpg = Property(
        float,
        get_mpg,
        set_mpg,
        notify=mpgChanged,
    )

    # ==================================================================
    # Fuel Level
    # ==================================================================

    def get_fuel_level(self) -> float:
        return self._fuel_level

    def set_fuel_level(self, value: float) -> None:
        value = max(
            0.0,
            min(100.0, float(value)),
        )

        if self._fuel_level == value:
            return

        self._fuel_level = value
        self.fuelLevelChanged.emit()

    fuelLevel = Property(
        float,
        get_fuel_level,
        set_fuel_level,
        notify=fuelLevelChanged,
    )

    # ==================================================================
    # Control Module Voltage
    # ==================================================================

    def get_voltage(self) -> float:
        return self._voltage

    def set_voltage(self, value: float) -> None:
        value = max(0.0, float(value))

        if self._voltage == value:
            return

        self._voltage = value
        self.voltageChanged.emit()

    voltage = Property(
        float,
        get_voltage,
        set_voltage,
        notify=voltageChanged,
    )

    # ==================================================================
    # Ambient Air Temperature
    # ==================================================================

    def get_air_temperature(self) -> float:
        return self._air_temperature

    def set_air_temperature(self, value: float) -> None:
        value = float(value)

        if self._air_temperature == value:
            return

        self._air_temperature = value
        self.airTemperatureChanged.emit()

    airTemperature = Property(
        float,
        get_air_temperature,
        set_air_temperature,
        notify=airTemperatureChanged,
    )

    # ==================================================================
    # Connection State
    # ==================================================================

    def get_connected(self) -> bool:
        return self._connected

    def set_connected(self, value: bool) -> None:
        value = bool(value)

        if self._connected == value:
            return

        self._connected = value
        self.connectedChanged.emit()

    connected = Property(
        bool,
        get_connected,
        set_connected,
        notify=connectedChanged,
    )

    # ==================================================================
    # Utility Methods
    # ==================================================================

    def reset(self) -> None:
        """
        Reset vehicle measurements and disconnect the vehicle.
        """

        self.set_rpm(0.0)
        self.set_speed(0.0)
        self.set_maf(0.0)
        self.set_mpg(0.0)
        self.set_fuel_level(0.0)
        self.set_voltage(0.0)
        self.set_air_temperature(0.0)

        self.set_connected(False)

    def clear_values(self) -> None:
        """
        Clear vehicle measurements without changing connection state.
        """

        self.set_rpm(0.0)
        self.set_speed(0.0)
        self.set_maf(0.0)
        self.set_mpg(0.0)
        self.set_fuel_level(0.0)
        self.set_voltage(0.0)
        self.set_air_temperature(0.0)

    def __repr__(self) -> str:
        return (
            "VehicleState("
            f"rpm={self._rpm}, "
            f"speed={self._speed}, "
            f"maf={self._maf}, "
            f"mpg={self._mpg}, "
            f"fuel_level={self._fuel_level}, "
            f"voltage={self._voltage}, "
            f"air_temperature={self._air_temperature}, "
            f"connected={self._connected}"
            ")"
        )
