# app/vehicle/vehicle_state.py

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Property, QObject, Signal


class VehicleState(QObject):
    """
    Represents the current state of the vehicle.

    VehicleState is intentionally independent of the OBD implementation.
    It does not communicate with the vehicle or perform OBD queries.

    Vehicle backends update this object, and QML observes its properties
    through Qt signals.

    Units:
        rpm:                    RPM
        speed:                  MPH
        maf:                    grams / second
        mpg:                    miles / gallon
        fuelLevel:              percent (0-100)
        voltage:                volts
        airTemperature:         degrees Fahrenheit
        troubleCodes:           stored diagnostic trouble codes
        pendingTroubleCodes:    pending diagnostic trouble codes

    Diagnostic trouble codes are represented as dictionaries:

        {
            "code": "P0300",
            "description": "Random/Multiple Cylinder Misfire Detected",
        }

    A code is kept in only one diagnostic list:

        - Stored codes are active/stored DTCs reported by Mode 03.
        - Pending codes are DTCs reported by Mode 07 that have not
          yet become stored.
        - If a code appears in both OBD responses, it is kept only
          in troubleCodes.
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

    troubleCodesChanged = Signal()
    pendingTroubleCodesChanged = Signal()

    connectedChanged = Signal()

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        super().__init__()

        self._rpm = 0.0
        self._speed = 0.0
        self._maf = 0.0
        self._mpg: float | None = 0.0
        self._fuel_level = 0.0
        self._voltage = 0.0
        self._air_temperature = 0.0

        self._trouble_codes: list[dict[str, str]] = []
        self._pending_trouble_codes: list[dict[str, str]] = []

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

    rpm = Property(float, get_rpm, set_rpm, notify=rpmChanged)

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

    speed = Property(float, get_speed, set_speed, notify=speedChanged)

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

    maf = Property(float, get_maf, set_maf, notify=mafChanged)

    # ==================================================================
    # Miles Per Gallon
    # ==================================================================

    def get_mpg(self) -> float | None:
        return self._mpg

    def set_mpg(self, value: float | None) -> None:
        if value is None:
            if self._mpg is None:
                return

            self._mpg = None
            self.mpgChanged.emit()
            return

        value = max(0.0, float(value))

        if self._mpg == value:
            return

        self._mpg = value
        self.mpgChanged.emit()

    mpg = Property("QVariant", get_mpg, set_mpg, notify=mpgChanged)

    # ==================================================================
    # Fuel Level
    # ==================================================================

    def get_fuel_level(self) -> float:
        return self._fuel_level

    def set_fuel_level(self, value: float) -> None:
        value = max(0.0, min(100.0, float(value)))

        if self._fuel_level == value:
            return

        self._fuel_level = value
        self.fuelLevelChanged.emit()

    fuelLevel = Property(float, get_fuel_level, set_fuel_level, notify=fuelLevelChanged)

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

    voltage = Property(float, get_voltage, set_voltage, notify=voltageChanged)

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

    airTemperature = Property(float, get_air_temperature, set_air_temperature, notify=airTemperatureChanged)

    # ==================================================================
    # Diagnostic Trouble Codes
    # ==================================================================

    @staticmethod
    def _normalize_codes(value: list[dict[str, Any]] | None) -> list[dict[str, str]]:
        """
        Normalize diagnostic trouble code dictionaries.

        Invalid entries are ignored.
        """

        normalized: list[dict[str, str]] = []

        if value is None:
            return normalized

        for item in value:
            if not isinstance(item, dict):
                continue

            code = item.get("code")

            if code is None:
                continue

            description = item.get("description")

            normalized.append({"code": str(code), "description": (str(description) if description is not None else "")})

        return normalized

    def get_trouble_codes(self) -> list[dict[str, str]]:
        """
        Return stored diagnostic trouble codes.
        """

        return self._trouble_codes

    def set_trouble_codes(self, value: list[dict[str, Any]] | None) -> None:
        """
        Update stored diagnostic trouble codes.

        Any matching pending codes are automatically removed from
        pendingTroubleCodes. A DTC should never appear in both lists.
        """

        normalized = self._normalize_codes(value)

        if self._trouble_codes == normalized:
            # Even if the stored list itself did not change, make sure
            # the pending list does not contain any of these codes.
            stored_codes = {item["code"] for item in normalized}

            if stored_codes:
                filtered_pending = [item for item in self._pending_trouble_codes if item["code"] not in stored_codes]

                if filtered_pending != self._pending_trouble_codes:
                    self._pending_trouble_codes = filtered_pending
                    self.pendingTroubleCodesChanged.emit()

            return

        self._trouble_codes = normalized
        self.troubleCodesChanged.emit()

        # A code cannot be both stored and pending.
        stored_codes = {item["code"] for item in normalized}

        if stored_codes:
            filtered_pending = [item for item in self._pending_trouble_codes if item["code"] not in stored_codes]

            if filtered_pending != self._pending_trouble_codes:
                self._pending_trouble_codes = filtered_pending
                self.pendingTroubleCodesChanged.emit()

    troubleCodes = Property("QVariantList", get_trouble_codes, set_trouble_codes, notify=troubleCodesChanged)

    # ==================================================================
    # Pending Diagnostic Trouble Codes
    # ==================================================================

    def get_pending_trouble_codes(self) -> list[dict[str, str]]:
        """
        Return pending diagnostic trouble codes.
        """

        return self._pending_trouble_codes

    def set_pending_trouble_codes(self, value: list[dict[str, Any]] | None) -> None:
        """
        Update pending diagnostic trouble codes.

        Any code already present in troubleCodes is removed from the
        pending list so that a code can never appear in both lists.
        """

        normalized = self._normalize_codes(value)

        # Stored codes take precedence over pending codes.
        stored_codes = {item["code"] for item in self._trouble_codes}

        if stored_codes:
            normalized = [item for item in normalized if item["code"] not in stored_codes]

        if self._pending_trouble_codes == normalized:
            return

        self._pending_trouble_codes = normalized
        self.pendingTroubleCodesChanged.emit()

    pendingTroubleCodes = Property("QVariantList", get_pending_trouble_codes, set_pending_trouble_codes, notify=pendingTroubleCodesChanged)

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

    connected = Property(bool, get_connected, set_connected, notify=connectedChanged)

    # ==================================================================
    # Utility Methods
    # ==================================================================

    def reset(self) -> None:
        """
        Reset all vehicle measurements and diagnostic state,
        and disconnect the vehicle.
        """

        self.set_rpm(0.0)
        self.set_speed(0.0)
        self.set_maf(0.0)
        self.set_mpg(0.0)
        self.set_fuel_level(0.0)
        self.set_voltage(0.0)
        self.set_air_temperature(0.0)

        self.set_trouble_codes([])
        self.set_pending_trouble_codes([])

        self.set_connected(False)

    def clear_values(self) -> None:
        """
        Clear vehicle measurements and diagnostic state without
        changing the connection state.
        """

        self.set_rpm(0.0)
        self.set_speed(0.0)
        self.set_maf(0.0)
        self.set_mpg(0.0)
        self.set_fuel_level(0.0)
        self.set_voltage(0.0)
        self.set_air_temperature(0.0)

        self.set_trouble_codes([])
        self.set_pending_trouble_codes([])

    def clear_diagnostic_codes(self) -> None:
        """
        Clear diagnostic codes from the local VehicleState.

        This does NOT clear codes from the actual vehicle ECU.

        Use OBDVehicle.clear_trouble_codes() to send the actual
        OBD clear-DTC command to the vehicle.
        """

        self.set_trouble_codes([])
        self.set_pending_trouble_codes([])

    # ==================================================================
    # Representation
    # ==================================================================

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
            f"trouble_codes={self._trouble_codes}, "
            f"pending_trouble_codes={self._pending_trouble_codes}, "
            f"connected={self._connected}"
            ")"
        )
