# app/settings/manager.py

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from PySide6.QtCore import Property, QObject, Signal

logger = logging.getLogger(__name__)


class SettingsManager(QObject):
    """
    Application settings manager.

    Settings are kept in memory while the application is running and
    persisted to a JSON file on disk.

    QML can read/write settings through Qt properties.

    Settings are divided into:

        rpm:
            min
            max
            redline
            shift

        shift_lights:
            enabled
            color1
            color2
            color3
            color4
            padding
    """

    COLOR_PALETTE_SIZE = 53
    BRIGHTNESS_MIN = 0
    BRIGHTNESS_MAX = 255

    # ================================================================
    # Signals
    # ================================================================

    rpmSettingsChanged = Signal()
    shiftLightSettingsChanged = Signal()
    settingsChanged = Signal()
    generalSettingsChanged = Signal()
    brightnessChanged = Signal()
    optimizeReadingsChanged = Signal()
    delayedReadingsChanged = Signal()

    def __init__(self) -> None:
        super().__init__()

        self._settings_path = self._get_settings_path()

        # ============================================================
        # RPM defaults
        # ============================================================

        self._rpm_min = 0
        self._rpm_max = 7000
        self._rpm_redline = 6500
        self._rpm_shift = 6000

        # ============================================================
        # Shift light defaults
        # ============================================================

        self._shift_lights_enabled = True

        # Indexes into the QML color palette.
        self._shift_light_color_1 = 12
        self._shift_light_color_2 = 8
        self._shift_light_color_3 = 4
        self._shift_light_color_4 = 0

        # RPM distance between each shift light.
        #
        # Example:
        #
        # shift RPM = 6000
        # padding   = 100
        #
        # start RPM = 6000 - (14 * 100)
        #           = 4600
        #
        self._shift_light_padding = 100

        # ============================================================
        # Customization defaults
        # ============================================================

        # Indexes into ColorPalette.colors.
        self._font1_color_index = 46
        self._font2_color_index = 47
        self._background1_color_index = 49
        self._background2_color_index = 50

        # Background image selection.
        self._background_image_index = 0

        # General settings
        self._brightness = self.BRIGHTNESS_MAX
        self._optimize_readings = False
        self._delayed_readings = False

        self._load()

    # ================================================================
    # Settings Path
    # ================================================================

    @staticmethod
    def _get_settings_path() -> Path:
        """
        Return the path used to store application settings.

        Linux:
            ~/.config/smart-dash/settings.json
        """

        config_dir = Path.home() / ".config" / "smart-dash"

        config_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        return config_dir / "settings.json"

    # ================================================================
    # RPM Minimum
    # ================================================================

    def get_rpm_min(self) -> int:
        return self._rpm_min

    def set_rpm_min(self, value: int) -> None:
        value = max(0, int(value))

        if self._rpm_min == value:
            return

        self._rpm_min = value

        self._validate()

        self.rpmSettingsChanged.emit()
        self.settingsChanged.emit()

        self.save()

    rpmMin = Property(
        int,
        get_rpm_min,
        set_rpm_min,
        notify=rpmSettingsChanged,
    )

    # ================================================================
    # RPM Maximum
    # ================================================================

    def get_rpm_max(self) -> int:
        return self._rpm_max

    def set_rpm_max(self, value: int) -> None:
        value = max(
            self._rpm_min,
            int(value),
        )

        if self._rpm_max == value:
            return

        self._rpm_max = value

        self._validate()

        self.rpmSettingsChanged.emit()
        self.settingsChanged.emit()

        self.save()

    rpmMax = Property(
        int,
        get_rpm_max,
        set_rpm_max,
        notify=rpmSettingsChanged,
    )

    # ================================================================
    # RPM Redline
    # ================================================================

    def get_rpm_redline(self) -> int:
        return self._rpm_redline

    def set_rpm_redline(self, value: int) -> None:
        value = max(
            self._rpm_min,
            min(
                self._rpm_max,
                int(value),
            ),
        )

        if self._rpm_redline == value:
            return

        self._rpm_redline = value

        self.rpmSettingsChanged.emit()
        self.settingsChanged.emit()

        self.save()

    rpmRedline = Property(
        int,
        get_rpm_redline,
        set_rpm_redline,
        notify=rpmSettingsChanged,
    )

    # ================================================================
    # RPM Shift Point
    # ================================================================

    def get_rpm_shift(self) -> int:
        return self._rpm_shift

    def set_rpm_shift(self, value: int) -> None:
        value = max(
            self._rpm_min,
            min(
                self._rpm_max,
                int(value),
            ),
        )

        if self._rpm_shift == value:
            return

        self._rpm_shift = value

        # Changing the shift RPM affects:
        #
        #   - RPM settings
        #   - shift-light thresholds
        #   - calculated shift-light starting RPM
        #
        self.rpmSettingsChanged.emit()
        self.shiftLightSettingsChanged.emit()
        self.settingsChanged.emit()

        self.save()

    rpmShift = Property(
        int,
        get_rpm_shift,
        set_rpm_shift,
        notify=rpmSettingsChanged,
    )

    # ================================================================
    # Shift Light Enabled
    # ================================================================

    def get_shift_lights_enabled(self) -> bool:
        return self._shift_lights_enabled

    def set_shift_lights_enabled(self, value: bool) -> None:
        value = bool(value)

        if self._shift_lights_enabled == value:
            return

        self._shift_lights_enabled = value

        self.shiftLightSettingsChanged.emit()
        self.settingsChanged.emit()

        self.save()

    shiftLightsEnabled = Property(
        bool,
        get_shift_lights_enabled,
        set_shift_lights_enabled,
        notify=shiftLightSettingsChanged,
    )

    # ================================================================
    # Shift Light Color 1
    # ================================================================

    def get_shift_light_color_1(self) -> int:
        return self._shift_light_color_1

    def set_shift_light_color_1(self, value: int) -> None:
        value = max(
            0,
            min(
                self.COLOR_PALETTE_SIZE - 1,
                int(value),
            ),
        )

        if self._shift_light_color_1 == value:
            return

        self._shift_light_color_1 = value

        self.shiftLightSettingsChanged.emit()
        self.settingsChanged.emit()

        self.save()

    shiftLightColor1 = Property(
        int,
        get_shift_light_color_1,
        set_shift_light_color_1,
        notify=shiftLightSettingsChanged,
    )

    # ================================================================
    # Shift Light Color 2
    # ================================================================

    def get_shift_light_color_2(self) -> int:
        return self._shift_light_color_2

    def set_shift_light_color_2(self, value: int) -> None:
        value = max(
            0,
            min(
                self.COLOR_PALETTE_SIZE - 1,
                int(value),
            ),
        )

        if self._shift_light_color_2 == value:
            return

        self._shift_light_color_2 = value

        self.shiftLightSettingsChanged.emit()
        self.settingsChanged.emit()

        self.save()

    shiftLightColor2 = Property(
        int,
        get_shift_light_color_2,
        set_shift_light_color_2,
        notify=shiftLightSettingsChanged,
    )

    # ================================================================
    # Shift Light Color 3
    # ================================================================

    def get_shift_light_color_3(self) -> int:
        return self._shift_light_color_3

    def set_shift_light_color_3(self, value: int) -> None:
        value = max(
            0,
            min(
                self.COLOR_PALETTE_SIZE - 1,
                int(value),
            ),
        )

        if self._shift_light_color_3 == value:
            return

        self._shift_light_color_3 = value

        self.shiftLightSettingsChanged.emit()
        self.settingsChanged.emit()

        self.save()

    shiftLightColor3 = Property(
        int,
        get_shift_light_color_3,
        set_shift_light_color_3,
        notify=shiftLightSettingsChanged,
    )

    # ================================================================
    # Shift Light Color 4
    # ================================================================

    def get_shift_light_color_4(self) -> int:
        return self._shift_light_color_4

    def set_shift_light_color_4(self, value: int) -> None:
        value = max(
            0,
            min(
                self.COLOR_PALETTE_SIZE - 1,
                int(value),
            ),
        )

        if self._shift_light_color_4 == value:
            return

        self._shift_light_color_4 = value

        self.shiftLightSettingsChanged.emit()
        self.settingsChanged.emit()

        self.save()

    shiftLightColor4 = Property(
        int,
        get_shift_light_color_4,
        set_shift_light_color_4,
        notify=shiftLightSettingsChanged,
    )

    # ================================================================
    # Shift Light Padding
    # ================================================================

    def get_shift_light_padding(self) -> int:
        return self._shift_light_padding

    def set_shift_light_padding(self, value: int) -> None:
        value = max(
            10,
            min(
                1000,
                int(value),
            ),
        )

        if self._shift_light_padding == value:
            return

        self._shift_light_padding = value

        self.shiftLightSettingsChanged.emit()
        self.settingsChanged.emit()

        self.save()

    shiftLightPadding = Property(
        int,
        get_shift_light_padding,
        set_shift_light_padding,
        notify=shiftLightSettingsChanged,
    )

    # ================================================================
    # Shift Light Starting RPM
    # ================================================================

    def get_shift_light_start_rpm(self) -> int:
        """
        Calculate the RPM at which the first shift light activates.

        There are 12 lights, with the original UI using:

            shift RPM - (14 * padding)

        This preserves the behavior of the old Pygame dashboard.
        """

        start_rpm = self._rpm_shift - (14 * self._shift_light_padding)

        return max(
            self._rpm_min,
            start_rpm,
        )

    shiftLightStartRpm = Property(
        int,
        get_shift_light_start_rpm,
        notify=shiftLightSettingsChanged,
    )

    # ================================================================
    # Font1 Color
    # ================================================================

    def get_font1_color_index(self) -> int:
        return self._font1_color_index

    def set_font1_color_index(self, value: int) -> None:
        value = max(
            0,
            min(
                self.COLOR_PALETTE_SIZE - 1,
                int(value),
            ),
        )

        if self._font1_color_index == value:
            return

        self._font1_color_index = value

        self.settingsChanged.emit()

        self.save()

    font1ColorIndex = Property(
        int,
        get_font1_color_index,
        set_font1_color_index,
        notify=settingsChanged,
    )

    # ================================================================
    # Font2 Color
    # ================================================================

    def get_font2_color_index(self) -> int:
        return self._font2_color_index

    def set_font2_color_index(self, value: int) -> None:
        value = max(
            0,
            min(
                self.COLOR_PALETTE_SIZE - 1,
                int(value),
            ),
        )

        if self._font2_color_index == value:
            return

        self._font2_color_index = value

        self.settingsChanged.emit()

        self.save()

    font2ColorIndex = Property(
        int,
        get_font2_color_index,
        set_font2_color_index,
        notify=settingsChanged,
    )

    # ================================================================
    # Background Color 1
    # ================================================================

    def get_background1_color_index(self) -> int:
        return self._background1_color_index

    def set_background1_color_index(self, value: int) -> None:
        value = max(
            0,
            min(
                self.COLOR_PALETTE_SIZE - 1,
                int(value),
            ),
        )

        if self._background1_color_index == value:
            return

        self._background1_color_index = value

        self.settingsChanged.emit()

        self.save()

    background1ColorIndex = Property(
        int,
        get_background1_color_index,
        set_background1_color_index,
        notify=settingsChanged,
    )

    # ================================================================
    # Background Color 2
    # ================================================================

    def get_background2_color_index(self) -> int:
        return self._background2_color_index

    def set_background2_color_index(self, value: int) -> None:
        value = max(
            0,
            min(
                self.COLOR_PALETTE_SIZE - 1,
                int(value),
            ),
        )

        if self._background2_color_index == value:
            return

        self._background2_color_index = value

        self.settingsChanged.emit()

        self.save()

    background2ColorIndex = Property(
        int,
        get_background2_color_index,
        set_background2_color_index,
        notify=settingsChanged,
    )

    # ================================================================
    # Background Image
    # ================================================================

    def get_background_image_index(self) -> int:
        return self._background_image_index

    def set_background_image_index(self, value: int) -> None:
        value = max(
            0,
            int(value),
        )

        if self._background_image_index == value:
            return

        self._background_image_index = value

        self.settingsChanged.emit()

        self.save()

    backgroundImageIndex = Property(
        int,
        get_background_image_index,
        set_background_image_index,
        notify=settingsChanged,
    )

    # ================================================================
    # Brightness
    # ================================================================

    def get_brightness(self) -> int:
        return self._brightness

    def set_brightness(self, value: int) -> None:
        value = max(
            self.BRIGHTNESS_MIN,
            min(
                self.BRIGHTNESS_MAX,
                int(value),
            ),
        )

        if self._brightness == value:
            return

        self._brightness = value

        self.brightnessChanged.emit()
        self.generalSettingsChanged.emit()
        self.settingsChanged.emit()

        self.save()

    brightness = Property(
        int,
        get_brightness,
        set_brightness,
        notify=brightnessChanged,
    )

    # ================================================================
    # Optimize Readings
    # ================================================================

    def get_optimize_readings(self) -> bool:
        return self._optimize_readings

    def set_optimize_readings(self, value: bool) -> None:
        value = bool(value)

        if self._optimize_readings == value:
            return

        self._optimize_readings = value

        self.optimizeReadingsChanged.emit()
        self.generalSettingsChanged.emit()
        self.settingsChanged.emit()

        self.save()

    optimizeReadings = Property(
        bool,
        get_optimize_readings,
        set_optimize_readings,
        notify=optimizeReadingsChanged,
    )

    # ================================================================
    # Delayed Readings
    # ================================================================

    def get_delayed_readings(self) -> bool:
        return self._delayed_readings

    def set_delayed_readings(self, value: bool) -> None:
        value = bool(value)

        if self._delayed_readings == value:
            return

        self._delayed_readings = value

        self.delayedReadingsChanged.emit()
        self.generalSettingsChanged.emit()
        self.settingsChanged.emit()

        self.save()

    delayedReadings = Property(
        bool,
        get_delayed_readings,
        set_delayed_readings,
        notify=delayedReadingsChanged,
    )

    # ================================================================
    # Load
    # ================================================================

    def _load(self) -> None:
        """
        Load settings from disk.

        Missing or invalid settings fall back to defaults.
        """

        if not self._settings_path.exists():
            logger.info("No settings file found. Using defaults.")
            return

        try:
            with self._settings_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

        except (OSError, json.JSONDecodeError) as exc:
            logger.warning(
                "Failed to load settings: %s",
                exc,
            )
            return

        rpm = data.get(
            "rpm",
            {},
        )

        shift_lights = data.get(
            "shift_lights",
            {},
        )

        # ============================================================
        # RPM
        # ============================================================

        self._rpm_min = int(
            rpm.get(
                "min",
                self._rpm_min,
            )
        )

        self._rpm_max = int(
            rpm.get(
                "max",
                self._rpm_max,
            )
        )

        self._rpm_redline = int(
            rpm.get(
                "redline",
                self._rpm_redline,
            )
        )

        self._rpm_shift = int(
            rpm.get(
                "shift",
                self._rpm_shift,
            )
        )

        # ============================================================
        # Shift Lights
        # ============================================================

        self._shift_lights_enabled = bool(
            shift_lights.get(
                "enabled",
                self._shift_lights_enabled,
            )
        )

        self._shift_light_color_1 = int(
            shift_lights.get(
                "color1",
                self._shift_light_color_1,
            )
        )

        self._shift_light_color_2 = int(
            shift_lights.get(
                "color2",
                self._shift_light_color_2,
            )
        )

        self._shift_light_color_3 = int(
            shift_lights.get(
                "color3",
                self._shift_light_color_3,
            )
        )

        self._shift_light_color_4 = int(
            shift_lights.get(
                "color4",
                self._shift_light_color_4,
            )
        )

        self._shift_light_padding = int(
            shift_lights.get(
                "padding",
                self._shift_light_padding,
            )
        )

        # ============================================================
        # Customization
        # ============================================================

        customization = data.get(
            "customization",
            {},
        )

        self._font1_color_index = int(
            customization.get(
                "font1_color",
                self._font1_color_index,
            )
        )

        self._font2_color_index = int(
            customization.get(
                "font2_color",
                self._font2_color_index,
            )
        )

        self._background1_color_index = int(
            customization.get(
                "background1_color",
                self._background1_color_index,
            )
        )

        self._background2_color_index = int(
            customization.get(
                "background2_color",
                self._background2_color_index,
            )
        )

        self._background_image_index = int(
            customization.get(
                "background_image",
                self._background_image_index,
            )
        )

        # ============================================================
        # General Settings
        # ============================================================

        general = data.get(
            "general",
            {},
        )

        self._brightness = int(
            general.get(
                "brightness",
                self._brightness,
            )
        )

        self._optimize_readings = bool(
            general.get(
                "optimize_readings",
                self._optimize_readings,
            )
        )

        self._delayed_readings = bool(
            general.get(
                "delayed_readings",
                self._delayed_readings,
            )
        )

        self._validate()

        logger.info(
            "Loaded settings from %s",
            self._settings_path,
        )

    # ================================================================
    # Validation
    # ================================================================

    def _validate(self) -> None:
        # ------------------------------------------------------------
        # RPM
        # ------------------------------------------------------------

        self._rpm_min = max(
            0,
            self._rpm_min,
        )

        self._rpm_max = max(
            self._rpm_min,
            self._rpm_max,
        )

        self._rpm_redline = max(
            self._rpm_min,
            min(
                self._rpm_max,
                self._rpm_redline,
            ),
        )

        self._rpm_shift = max(
            self._rpm_min,
            min(
                self._rpm_max,
                self._rpm_shift,
            ),
        )

        # ------------------------------------------------------------
        # Shift light colors
        # ------------------------------------------------------------

        self._shift_light_color_1 = max(
            0,
            min(
                self.COLOR_PALETTE_SIZE - 1,
                self._shift_light_color_1,
            ),
        )

        self._shift_light_color_2 = max(
            0,
            min(
                self.COLOR_PALETTE_SIZE - 1,
                self._shift_light_color_2,
            ),
        )

        self._shift_light_color_3 = max(
            0,
            min(
                self.COLOR_PALETTE_SIZE - 1,
                self._shift_light_color_3,
            ),
        )

        self._shift_light_color_4 = max(
            0,
            min(
                self.COLOR_PALETTE_SIZE - 1,
                self._shift_light_color_4,
            ),
        )

        # ------------------------------------------------------------
        # Shift light padding
        # ------------------------------------------------------------

        self._shift_light_padding = max(
            10,
            min(
                1000,
                self._shift_light_padding,
            ),
        )

        # ------------------------------------------------------------
        # Customization colors
        # ------------------------------------------------------------

        self._font1_color_index = max(
            0,
            min(
                self.COLOR_PALETTE_SIZE - 1,
                self._font1_color_index,
            ),
        )

        self._font2_color_index = max(
            0,
            min(
                self.COLOR_PALETTE_SIZE - 1,
                self._font2_color_index,
            ),
        )

        self._background1_color_index = max(
            0,
            min(
                self.COLOR_PALETTE_SIZE - 1,
                self._background1_color_index,
            ),
        )

        self._background2_color_index = max(
            0,
            min(
                self.COLOR_PALETTE_SIZE - 1,
                self._background2_color_index,
            ),
        )

        self._background_image_index = max(
            0,
            self._background_image_index,
        )

        # ------------------------------------------------------------
        # General settings
        # ------------------------------------------------------------

        self._brightness = max(
            self.BRIGHTNESS_MIN,
            min(
                self.BRIGHTNESS_MAX,
                self._brightness,
            ),
        )

        self._optimize_readings = bool(self._optimize_readings)

        self._delayed_readings = bool(self._delayed_readings)

    # ================================================================
    # Save
    # ================================================================

    def save(self) -> None:
        """
        Persist all settings to disk.

        Uses a temporary file and atomic replacement so that a
        partially-written settings file is avoided if the application
        is interrupted during a save.
        """

        data: dict[str, Any] = {
            "rpm": {
                "min": self._rpm_min,
                "max": self._rpm_max,
                "redline": self._rpm_redline,
                "shift": self._rpm_shift,
            },
            "shift_lights": {
                "enabled": self._shift_lights_enabled,
                "color1": self._shift_light_color_1,
                "color2": self._shift_light_color_2,
                "color3": self._shift_light_color_3,
                "color4": self._shift_light_color_4,
                "padding": self._shift_light_padding,
            },
            "customization": {
                "font1_color": self._font1_color_index,
                "font2_color": self._font2_color_index,
                "background1_color": self._background1_color_index,
                "background2_color": self._background2_color_index,
                "background_image": self._background_image_index,
            },
            "general": {
                "brightness": self._brightness,
                "optimize_readings": self._optimize_readings,
                "delayed_readings": self._delayed_readings,
            },
        }

        try:
            self._settings_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            temporary_path = self._settings_path.with_suffix(".tmp")

            with temporary_path.open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    data,
                    file,
                    indent=4,
                )

                file.write("\n")

            temporary_path.replace(self._settings_path)

            logger.debug(
                "Saved settings to %s",
                self._settings_path,
            )

        except OSError as exc:
            logger.error(
                "Failed to save settings: %s",
                exc,
            )
