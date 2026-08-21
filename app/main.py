# app/main.py

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from app.settings.manager import SettingsManager
from app.vehicle.vehicle_state import VehicleState

# =====================================================================
# Logging
# =====================================================================

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

logger = logging.getLogger(__name__)


# =====================================================================
# Vehicle Backend
# =====================================================================


def create_vehicle_backend(vehicle: VehicleState):
    """
    Create the vehicle backend selected by VEHICLE_MODE.

    Supported modes:

        simulator
            Uses VehicleSimulator and generates simulated vehicle data.

        obd
            Uses OBDVehicle and attempts to communicate with a real
            OBD-II adapter.

    Returns:
        The selected vehicle backend.
    """

    vehicle_mode = os.getenv("VEHICLE_MODE", "simulator").strip().lower()

    logger.info("Vehicle mode: %s", vehicle_mode)

    # ---------------------------------------------------------------
    # Simulator
    # ---------------------------------------------------------------

    if vehicle_mode == "simulator":
        from app.vehicle.simulator import VehicleSimulator

        logger.info("Using vehicle simulator.")

        return VehicleSimulator(vehicle)

    # ---------------------------------------------------------------
    # Real OBD-II Vehicle
    # ---------------------------------------------------------------

    if vehicle_mode == "obd":
        from app.vehicle.obd import OBDVehicle

        logger.info("Using real OBD vehicle backend.")

        return OBDVehicle(vehicle)

    # ---------------------------------------------------------------
    # Invalid Mode
    # ---------------------------------------------------------------

    raise ValueError(f"Unknown VEHICLE_MODE: {vehicle_mode!r}. Expected 'simulator' or 'obd'.")


# =====================================================================
# Main
# =====================================================================


def main() -> int:
    """
    Start the Smart Dash application.
    """

    logger.info("Starting Smart Dash.")

    # ---------------------------------------------------------------
    # Qt Application
    # ---------------------------------------------------------------

    app = QGuiApplication(sys.argv)

    # ---------------------------------------------------------------
    # Vehicle State
    # ---------------------------------------------------------------
    #
    # VehicleState is shared between the vehicle backend and QML.
    #
    # The backend writes values into VehicleState.
    #
    # QML observes VehicleState through Qt properties and signals.
    #

    vehicle = VehicleState()

    # ---------------------------------------------------------------
    # Settings
    # ---------------------------------------------------------------
    #
    # SettingsManager:
    #
    # - Loads settings from:
    #
    #       ~/.config/smart-dash/settings.json
    #
    # - Exposes settings to QML.
    #
    # - Automatically saves changes.
    #

    settings_manager = SettingsManager()

    # ---------------------------------------------------------------
    # Vehicle Backend
    # ---------------------------------------------------------------
    #
    # The backend is selected using:
    #
    #     VEHICLE_MODE=simulator
    #
    # or:
    #
    #     VEHICLE_MODE=obd
    #
    # QML does not need to know which mode is active.
    #
    # It interacts with:
    #
    #     vehicle
    #     vehicleBackend
    #
    # ---------------------------------------------------------------

    try:
        vehicle_backend = create_vehicle_backend(vehicle)

    except ValueError as exc:
        logger.error("%s", exc)

        return 1

    # ---------------------------------------------------------------
    # QML Engine
    # ---------------------------------------------------------------

    engine = QQmlApplicationEngine()

    # ---------------------------------------------------------------
    # Expose Python Objects to QML
    # ---------------------------------------------------------------
    #
    # vehicle:
    #
    #     Current vehicle state.
    #
    # vehicleBackend:
    #
    #     Active vehicle implementation.
    #
    #     This can be either:
    #
    #         VehicleSimulator
    #
    #     or:
    #
    #         OBDVehicle
    #
    # settingsManager:
    #
    #     Application settings.
    #
    # ---------------------------------------------------------------

    engine.rootContext().setContextProperty("vehicle", vehicle)

    engine.rootContext().setContextProperty("vehicleBackend", vehicle_backend)

    engine.rootContext().setContextProperty("settingsManager", settings_manager)

    # ---------------------------------------------------------------
    # Backwards Compatibility
    # ---------------------------------------------------------------
    #
    # Some existing QML files may still use "settings".
    #
    # Keep this alias while the application is being migrated.
    #

    engine.rootContext().setContextProperty("settings", settings_manager)

    # ---------------------------------------------------------------
    # Start Vehicle Backend
    # ---------------------------------------------------------------

    try:
        vehicle_backend.start()

    except Exception as exc:
        logger.exception("Failed to start vehicle backend.")

        logger.error("Vehicle backend error: %s", exc)

        return 1

    # ---------------------------------------------------------------
    # QML File
    # ---------------------------------------------------------------

    qml_file = Path(__file__).resolve().parent / "ui" / "qml" / "Main.qml"

    logger.debug("Loading QML: %s", qml_file)

    if not qml_file.exists():
        logger.error("Main.qml not found: %s", qml_file)

        try:
            vehicle_backend.stop()
        except Exception:
            logger.exception("Error while stopping vehicle backend.")

        return 1

    # ---------------------------------------------------------------
    # Load QML
    # ---------------------------------------------------------------

    engine.load(QUrl.fromLocalFile(str(qml_file)))

    # ---------------------------------------------------------------
    # Verify QML Loaded
    # ---------------------------------------------------------------

    if not engine.rootObjects():
        logger.error("Failed to load QML application.")

        try:
            vehicle_backend.stop()
        except Exception:
            logger.exception("Error while stopping vehicle backend.")

        return 1

    logger.info("Smart Dash UI loaded successfully.")

    # ---------------------------------------------------------------
    # Run Application
    # ---------------------------------------------------------------

    try:
        exit_code = app.exec()

    finally:
        # -----------------------------------------------------------
        # Cleanup
        # -----------------------------------------------------------

        logger.info("Stopping vehicle backend.")

        try:
            vehicle_backend.stop()

        except Exception:
            logger.exception("Error while stopping vehicle backend.")

        logger.info("Smart Dash stopped.")

    return exit_code


# =====================================================================
# Entry Point
# =====================================================================

if __name__ == "__main__":
    sys.exit(main())
