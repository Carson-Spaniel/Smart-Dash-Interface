# app/main.py

from __future__ import annotations

import logging
import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from app.settings.manager import SettingsManager
from app.vehicle.simulator import VehicleSimulator
from app.vehicle.vehicle_state import VehicleState

# =====================================================================
# Logging
# =====================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


# =====================================================================
# Main
# =====================================================================


def main() -> int:
    """Start the Smart Dash application."""

    logger.info("Starting Smart Dash")

    # ---------------------------------------------------------------
    # Qt Application
    # ---------------------------------------------------------------

    app = QGuiApplication(sys.argv)

    # ---------------------------------------------------------------
    # Vehicle State
    # ---------------------------------------------------------------
    #
    # VehicleState contains the current vehicle measurements.
    #
    # QML observes this object through Qt properties/signals.
    #

    vehicle = VehicleState()

    # ---------------------------------------------------------------
    # Settings
    # ---------------------------------------------------------------
    #
    # SettingsManager:
    #
    # - Loads settings from:
    #       ~/.config/smart-dash/settings.json
    #
    # - Exposes settings to QML.
    #
    # - Automatically saves changes.
    #
    # - Keeps settings available for the entire application lifetime.
    #

    settings_manager = SettingsManager()

    # ---------------------------------------------------------------
    # Vehicle Simulator
    # ---------------------------------------------------------------
    #
    # The simulator writes simulated vehicle data into VehicleState.
    #
    # When the real OBD implementation is ready, this can be replaced
    # with the real vehicle data source.
    #

    simulator = VehicleSimulator(vehicle)

    logger.info("Using vehicle simulator.")

    # ---------------------------------------------------------------
    # QML Engine
    # ---------------------------------------------------------------

    engine = QQmlApplicationEngine()

    # ---------------------------------------------------------------
    # Expose Python Objects to QML
    # ---------------------------------------------------------------
    #
    # IMPORTANT:
    #
    # The QML UI expects:
    #
    #     vehicle
    #     settingsManager
    #
    # We expose both "settingsManager" and the older "settings" name.
    #
    # "settingsManager" is the preferred name going forward.
    #

    engine.rootContext().setContextProperty(
        "vehicle",
        vehicle,
    )

    engine.rootContext().setContextProperty(
        "settingsManager",
        settings_manager,
    )

    # Backwards compatibility for older QML files that use "settings".
    engine.rootContext().setContextProperty(
        "settings",
        settings_manager,
    )

    # ---------------------------------------------------------------
    # Start Vehicle Source
    # ---------------------------------------------------------------
    #
    # Start the simulator before loading QML so the dashboard has a
    # live VehicleState immediately.
    #

    simulator.start()

    # ---------------------------------------------------------------
    # QML File
    # ---------------------------------------------------------------

    qml_file = Path(__file__).resolve().parent / "ui" / "qml" / "Main.qml"

    logger.debug(
        "Loading QML: %s",
        qml_file,
    )

    if not qml_file.exists():
        logger.error(
            "Main.qml not found: %s",
            qml_file,
        )

        simulator.stop()

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

        simulator.stop()

        return 1

    logger.info("Smart Dash UI loaded successfully.")

    # ---------------------------------------------------------------
    # Run Application
    # ---------------------------------------------------------------

    exit_code = app.exec()

    # ---------------------------------------------------------------
    # Cleanup
    # ---------------------------------------------------------------

    simulator.stop()

    logger.info("Smart Dash stopped.")

    return exit_code


# =====================================================================
# Entry Point
# =====================================================================

if __name__ == "__main__":
    sys.exit(main())
