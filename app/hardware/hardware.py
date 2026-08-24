# app/hardware/hardware.py

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QObject

from app.settings.manager import SettingsManager

logger = logging.getLogger(__name__)


class HardwareManager(QObject):
    """
    Manages physical hardware associated with the application.

    SettingsManager owns the desired application settings.

    HardwareManager listens for hardware-related setting changes and
    applies those settings to the physical hardware.

    Currently supported:
        - Display brightness

    Brightness is represented by SettingsManager as a value from:

        0   = minimum brightness
        255 = maximum brightness

    Linux backlight devices may use a different range internally, so
    the configured 0-255 value is converted to the hardware's native
    range before being written.
    """

    def __init__(self, settings_manager: SettingsManager) -> None:
        super().__init__()

        self._settings = settings_manager

        # ============================================================
        # Settings Connections
        # ============================================================

        self._settings.brightnessChanged.connect(self._on_brightness_changed)

        # ============================================================
        # Initial Hardware State
        # ============================================================

        self._apply_settings()

    # ==================================================================
    # Settings
    # ==================================================================

    def _apply_settings(self) -> None:
        """
        Apply the current hardware-related settings.

        This is called once during initialization so that the physical
        hardware immediately matches the saved application settings.
        """

        self._apply_brightness(self._settings.brightness)

    # ==================================================================
    # Brightness
    # ==================================================================

    def _on_brightness_changed(self) -> None:
        """
        Called whenever the configured brightness changes.
        """

        self._apply_brightness(self._settings.brightness)

    def _apply_brightness(self, value: int) -> None:
        """
        Apply brightness to the physical display.

        SettingsManager stores brightness in the range:

            0 - 255

        Linux backlight devices commonly expose a different native
        range, such as:

            0 - 100
            0 - 200
            0 - 937

        The value is therefore converted to the range reported by
        max_brightness.
        """

        value = max(SettingsManager.BRIGHTNESS_MIN, min(SettingsManager.BRIGHTNESS_MAX, int(value)))

        brightness_path = self._find_brightness_device()

        if brightness_path is None:
            logger.warning("No Linux backlight device found. Brightness %d was not applied.", value)
            return

        max_brightness_path = brightness_path.parent / "max_brightness"

        max_brightness = self._read_max_brightness(max_brightness_path)

        if max_brightness is None:
            return

        hardware_value = self._convert_brightness(value, max_brightness)

        if not self._write_brightness(brightness_path, hardware_value):
            return

        logger.debug("Brightness applied: %d/255 -> %d/%d", value, hardware_value, max_brightness)

    # ==================================================================
    # Brightness Conversion
    # ==================================================================

    @staticmethod
    def _convert_brightness(value: int, max_brightness: int) -> int:
        """
        Convert application brightness from 0-255 to the hardware's
        native brightness range.
        """

        if max_brightness <= 0:
            return 0

        hardware_value = round(value * max_brightness / SettingsManager.BRIGHTNESS_MAX)

        return max(0, min(max_brightness, hardware_value))

    # ==================================================================
    # Linux Backlight
    # ==================================================================

    @staticmethod
    def _find_brightness_device() -> Path | None:
        """
        Find a usable Linux backlight device.

        Linux normally exposes backlight devices through:

            /sys/class/backlight/

        A typical device looks like:

            /sys/class/backlight/intel_backlight/
                brightness
                max_brightness
                actual_brightness
                ...

        Returns:
            Path to the brightness file, or None if no suitable device
            could be found.
        """

        backlight_directory = Path("/sys/class/backlight")

        if not backlight_directory.exists():
            logger.debug("Linux backlight directory does not exist: %s", backlight_directory)
            return None

        try:
            devices = sorted(backlight_directory.iterdir())

        except OSError as exc:
            logger.error("Failed to inspect Linux backlight directory %s: %s", backlight_directory, exc)
            return None

        for device in devices:
            if not device.is_dir():
                continue

            brightness_path = device / "brightness"

            max_brightness_path = device / "max_brightness"

            if not brightness_path.exists():
                continue

            if not max_brightness_path.exists():
                continue

            logger.debug("Using Linux backlight device: %s", device)

            return brightness_path

        logger.debug("No usable Linux backlight devices found.")

        return None

    @staticmethod
    def _read_max_brightness(path: Path) -> int | None:
        """
        Read the maximum brightness supported by a Linux backlight
        device.
        """

        try:
            value = int(path.read_text(encoding="utf-8").strip())

        except (OSError, ValueError) as exc:
            logger.error("Failed to read max brightness from %s: %s", path, exc)
            return None

        if value <= 0:
            logger.error("Invalid max brightness value from %s: %d", path, value)
            return None

        return value

    @staticmethod
    def _write_brightness(path: Path, value: int) -> bool:
        """
        Write a brightness value to the Linux backlight device.
        """

        try:
            path.write_text(str(value), encoding="utf-8")

        except OSError as exc:
            logger.error("Failed to write brightness value %d to %s: %s", value, path, exc)
            return False

        return True
