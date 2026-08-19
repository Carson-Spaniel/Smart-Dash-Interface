from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.hardware.hardware import HardwareManager
from app.settings.manager import SettingsManager

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def settings_manager():
    settings = MagicMock(spec=SettingsManager)
    settings.brightness = 128
    settings.brightnessChanged = MagicMock()
    settings.brightnessChanged.connect = MagicMock()
    return settings


@pytest.fixture
def hardware_manager(settings_manager):
    with patch.object(
        HardwareManager,
        "_apply_settings",
    ):
        manager = HardwareManager(settings_manager)

    return manager


# ---------------------------------------------------------------------------
# Initialization / settings
# ---------------------------------------------------------------------------


def test_initializes_with_settings_manager(settings_manager):
    with patch.object(
        HardwareManager,
        "_apply_settings",
    ) as apply_settings:
        manager = HardwareManager(settings_manager)

    assert manager._settings is settings_manager

    settings_manager.brightnessChanged.connect.assert_called_once_with(
        manager._on_brightness_changed
    )

    apply_settings.assert_called_once_with()


def test_apply_settings_applies_current_brightness(
    hardware_manager,
    settings_manager,
):
    with patch.object(
        hardware_manager,
        "_apply_brightness",
    ) as apply_brightness:
        hardware_manager._apply_settings()

    apply_brightness.assert_called_once_with(settings_manager.brightness)


def test_brightness_changed_applies_current_brightness(
    hardware_manager,
    settings_manager,
):
    settings_manager.brightness = 200

    with patch.object(
        hardware_manager,
        "_apply_brightness",
    ) as apply_brightness:
        hardware_manager._on_brightness_changed()

    apply_brightness.assert_called_once_with(200)


# ---------------------------------------------------------------------------
# Brightness conversion
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "max_brightness", "expected"),
    [
        (0, 100, 0),
        (255, 100, 100),
        (128, 100, 50),
        (64, 100, 25),
        (255, 200, 200),
        (128, 200, 100),
        (128, 937, 470),
        (255, 937, 937),
    ],
)
def test_convert_brightness(
    value,
    max_brightness,
    expected,
):
    assert (
        HardwareManager._convert_brightness(
            value,
            max_brightness,
        )
        == expected
    )


@pytest.mark.parametrize(
    "max_brightness",
    [
        0,
        -1,
        -100,
    ],
)
def test_convert_brightness_returns_zero_for_invalid_max(
    max_brightness,
):
    assert (
        HardwareManager._convert_brightness(
            128,
            max_brightness,
        )
        == 0
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (-100, 0),
        (-1, 0),
        (0, 0),
        (255, 255),
        (256, 255),
        (1000, 255),
    ],
)
def test_convert_brightness_clamps_result(
    value,
    expected,
):
    assert (
        HardwareManager._convert_brightness(
            value,
            255,
        )
        == expected
    )


def test_convert_brightness_rounds_to_nearest_integer():
    # 128 * 100 / 255 = 50.196...
    assert (
        HardwareManager._convert_brightness(
            128,
            100,
        )
        == 50
    )

    # 129 * 100 / 255 = 50.588...
    assert (
        HardwareManager._convert_brightness(
            129,
            100,
        )
        == 51
    )


# ---------------------------------------------------------------------------
# Finding Linux backlight devices
# ---------------------------------------------------------------------------


def test_find_brightness_device_returns_none_when_directory_missing():
    directory = MagicMock()
    directory.exists.return_value = False

    with patch(
        "app.hardware.hardware.Path",
        return_value=directory,
    ):
        result = HardwareManager._find_brightness_device()

    assert result is None
    directory.exists.assert_called_once_with()


def test_find_brightness_device_handles_directory_os_error():
    directory = MagicMock()
    directory.exists.return_value = True
    directory.iterdir.side_effect = OSError("permission denied")

    with patch(
        "app.hardware.hardware.Path",
        return_value=directory,
    ):
        result = HardwareManager._find_brightness_device()

    assert result is None


def test_find_brightness_device_skips_non_directories():
    directory = MagicMock()

    non_directory = MagicMock()
    non_directory.is_dir.return_value = False

    directory.exists.return_value = True
    directory.iterdir.return_value = [non_directory]

    with patch(
        "app.hardware.hardware.Path",
        return_value=directory,
    ):
        result = HardwareManager._find_brightness_device()

    assert result is None
    non_directory.is_dir.assert_called_once_with()


def test_find_brightness_device_skips_device_without_brightness_file():
    directory = MagicMock()

    device = MagicMock()
    device.is_dir.return_value = True

    brightness_path = MagicMock()
    brightness_path.exists.return_value = False

    max_brightness_path = MagicMock()
    max_brightness_path.exists.return_value = True

    def divide(value):
        if value == "brightness":
            return brightness_path

        if value == "max_brightness":
            return max_brightness_path

        raise AssertionError(f"Unexpected path component: {value}")

    device.__truediv__.side_effect = divide

    directory.exists.return_value = True
    directory.iterdir.return_value = [device]

    with patch(
        "app.hardware.hardware.Path",
        return_value=directory,
    ):
        result = HardwareManager._find_brightness_device()

    assert result is None

    brightness_path.exists.assert_called_once_with()
    max_brightness_path.exists.assert_not_called()


def test_find_brightness_device_skips_device_without_max_brightness_file():
    directory = MagicMock()

    device = MagicMock()
    device.is_dir.return_value = True

    brightness_path = MagicMock()
    brightness_path.exists.return_value = True

    max_brightness_path = MagicMock()
    max_brightness_path.exists.return_value = False

    def divide(value):
        if value == "brightness":
            return brightness_path

        if value == "max_brightness":
            return max_brightness_path

        raise AssertionError(f"Unexpected path component: {value}")

    device.__truediv__.side_effect = divide

    directory.exists.return_value = True
    directory.iterdir.return_value = [device]

    with patch(
        "app.hardware.hardware.Path",
        return_value=directory,
    ):
        result = HardwareManager._find_brightness_device()

    assert result is None

    brightness_path.exists.assert_called_once_with()
    max_brightness_path.exists.assert_called_once_with()


def test_find_brightness_device_returns_first_usable_device():
    directory = MagicMock()

    device = MagicMock()
    device.is_dir.return_value = True

    brightness_path = MagicMock()
    brightness_path.exists.return_value = True

    max_brightness_path = MagicMock()
    max_brightness_path.exists.return_value = True

    def divide(value):
        if value == "brightness":
            return brightness_path

        if value == "max_brightness":
            return max_brightness_path

        raise AssertionError(f"Unexpected path component: {value}")

    device.__truediv__.side_effect = divide

    directory.exists.return_value = True
    directory.iterdir.return_value = [device]

    with patch(
        "app.hardware.hardware.Path",
        return_value=directory,
    ):
        result = HardwareManager._find_brightness_device()

    assert result is brightness_path


def test_find_brightness_device_skips_invalid_devices_until_usable_one():
    """
    Verify that an invalid device is skipped and a later valid device
    is returned.

    Real Path objects are used for the devices so that sorted() behaves
    exactly as it does with real filesystem paths.
    """
    invalid_device = Path("/sys/class/backlight/invalid")

    valid_device = Path("/sys/class/backlight/valid")

    directory = MagicMock()
    directory.exists.return_value = True

    # Deliberately put them in reverse order. The production code calls
    # sorted(), so the invalid device should still be inspected first.
    directory.iterdir.return_value = [
        valid_device,
        invalid_device,
    ]

    def is_dir_side_effect(path):
        return path in {
            invalid_device,
            valid_device,
        }

    def exists_side_effect(path):
        if path == invalid_device / "brightness":
            return False

        if path == invalid_device / "max_brightness":
            return True

        if path == valid_device / "brightness":
            return True

        if path == valid_device / "max_brightness":
            return True

        return False

    with (
        patch(
            "app.hardware.hardware.Path",
            return_value=directory,
        ),
        patch.object(
            Path,
            "is_dir",
            autospec=True,
            side_effect=is_dir_side_effect,
        ),
        patch.object(
            Path,
            "exists",
            autospec=True,
            side_effect=exists_side_effect,
        ),
    ):
        result = HardwareManager._find_brightness_device()

    assert result == valid_device / "brightness"


# ---------------------------------------------------------------------------
# Reading max brightness
# ---------------------------------------------------------------------------


def test_read_max_brightness_returns_integer(tmp_path):
    path = tmp_path / "max_brightness"

    path.write_text(
        "937\n",
        encoding="utf-8",
    )

    assert HardwareManager._read_max_brightness(path) == 937


def test_read_max_brightness_strips_whitespace(tmp_path):
    path = tmp_path / "max_brightness"

    path.write_text(
        "  200  \n",
        encoding="utf-8",
    )

    assert HardwareManager._read_max_brightness(path) == 200


@pytest.mark.parametrize(
    "contents",
    [
        "",
        "not-a-number",
        "12.5",
        "abc123",
    ],
)
def test_read_max_brightness_returns_none_for_invalid_content(
    tmp_path,
    contents,
):
    path = tmp_path / "max_brightness"

    path.write_text(
        contents,
        encoding="utf-8",
    )

    assert HardwareManager._read_max_brightness(path) is None


@pytest.mark.parametrize(
    "contents",
    [
        "0",
        "-1",
        "-100",
    ],
)
def test_read_max_brightness_returns_none_for_non_positive_value(
    tmp_path,
    contents,
):
    path = tmp_path / "max_brightness"

    path.write_text(
        contents,
        encoding="utf-8",
    )

    assert HardwareManager._read_max_brightness(path) is None


def test_read_max_brightness_returns_none_on_os_error(tmp_path):
    path = tmp_path / "max_brightness"

    with patch.object(
        Path,
        "read_text",
        side_effect=OSError("permission denied"),
    ):
        result = HardwareManager._read_max_brightness(path)

    assert result is None


# ---------------------------------------------------------------------------
# Writing brightness
# ---------------------------------------------------------------------------


def test_write_brightness_writes_value(tmp_path):
    path = tmp_path / "brightness"

    result = HardwareManager._write_brightness(
        path,
        127,
    )

    assert result is True

    assert path.read_text(encoding="utf-8") == "127"


def test_write_brightness_writes_zero(tmp_path):
    path = tmp_path / "brightness"

    result = HardwareManager._write_brightness(
        path,
        0,
    )

    assert result is True

    assert path.read_text(encoding="utf-8") == "0"


def test_write_brightness_returns_false_on_os_error(
    tmp_path,
):
    path = tmp_path / "brightness"

    with patch.object(
        Path,
        "write_text",
        side_effect=OSError("permission denied"),
    ):
        result = HardwareManager._write_brightness(
            path,
            100,
        )

    assert result is False


# ---------------------------------------------------------------------------
# Applying brightness
# ---------------------------------------------------------------------------


def test_apply_brightness_does_nothing_when_no_device(
    hardware_manager,
):
    with (
        patch.object(
            HardwareManager,
            "_find_brightness_device",
            return_value=None,
        ),
        patch.object(
            HardwareManager,
            "_read_max_brightness",
        ) as read_max,
        patch.object(
            HardwareManager,
            "_write_brightness",
        ) as write_brightness,
    ):
        hardware_manager._apply_brightness(128)

    read_max.assert_not_called()
    write_brightness.assert_not_called()


def test_apply_brightness_clamps_value_before_hardware_application(
    hardware_manager,
):
    brightness_path = Path("/sys/class/backlight/test/brightness")

    with (
        patch.object(
            HardwareManager,
            "_find_brightness_device",
            return_value=brightness_path,
        ),
        patch.object(
            HardwareManager,
            "_read_max_brightness",
            return_value=100,
        ),
        patch.object(
            HardwareManager,
            "_write_brightness",
            return_value=True,
        ) as write_brightness,
    ):
        hardware_manager._apply_brightness(999)

    write_brightness.assert_called_once_with(
        brightness_path,
        100,
    )


def test_apply_brightness_clamps_negative_value(
    hardware_manager,
):
    brightness_path = Path("/sys/class/backlight/test/brightness")

    with (
        patch.object(
            HardwareManager,
            "_find_brightness_device",
            return_value=brightness_path,
        ),
        patch.object(
            HardwareManager,
            "_read_max_brightness",
            return_value=100,
        ),
        patch.object(
            HardwareManager,
            "_write_brightness",
            return_value=True,
        ) as write_brightness,
    ):
        hardware_manager._apply_brightness(-50)

    write_brightness.assert_called_once_with(
        brightness_path,
        0,
    )


def test_apply_brightness_reads_max_brightness_from_sibling_file(
    hardware_manager,
):
    brightness_path = Path("/sys/class/backlight/test/brightness")

    max_brightness_path = Path("/sys/class/backlight/test/max_brightness")

    with (
        patch.object(
            HardwareManager,
            "_find_brightness_device",
            return_value=brightness_path,
        ),
        patch.object(
            HardwareManager,
            "_read_max_brightness",
            return_value=200,
        ) as read_max,
        patch.object(
            HardwareManager,
            "_write_brightness",
            return_value=True,
        ),
    ):
        hardware_manager._apply_brightness(128)

    read_max.assert_called_once_with(max_brightness_path)


def test_apply_brightness_converts_and_writes_value(
    hardware_manager,
):
    brightness_path = Path("/sys/class/backlight/test/brightness")

    with (
        patch.object(
            HardwareManager,
            "_find_brightness_device",
            return_value=brightness_path,
        ),
        patch.object(
            HardwareManager,
            "_read_max_brightness",
            return_value=100,
        ),
        patch.object(
            HardwareManager,
            "_write_brightness",
            return_value=True,
        ) as write_brightness,
    ):
        hardware_manager._apply_brightness(128)

    write_brightness.assert_called_once_with(
        brightness_path,
        50,
    )


def test_apply_brightness_does_not_write_when_max_brightness_is_invalid(
    hardware_manager,
):
    brightness_path = Path("/sys/class/backlight/test/brightness")

    with (
        patch.object(
            HardwareManager,
            "_find_brightness_device",
            return_value=brightness_path,
        ),
        patch.object(
            HardwareManager,
            "_read_max_brightness",
            return_value=None,
        ),
        patch.object(
            HardwareManager,
            "_write_brightness",
        ) as write_brightness,
    ):
        hardware_manager._apply_brightness(128)

    write_brightness.assert_not_called()


def test_apply_brightness_does_not_log_success_when_write_fails(
    hardware_manager,
    caplog,
):
    brightness_path = Path("/sys/class/backlight/test/brightness")

    with (
        patch.object(
            HardwareManager,
            "_find_brightness_device",
            return_value=brightness_path,
        ),
        patch.object(
            HardwareManager,
            "_read_max_brightness",
            return_value=100,
        ),
        patch.object(
            HardwareManager,
            "_write_brightness",
            return_value=False,
        ),
    ):
        hardware_manager._apply_brightness(128)

    assert "Brightness applied" not in caplog.text


# ---------------------------------------------------------------------------
# End-to-end-ish application flow
# ---------------------------------------------------------------------------


def test_brightness_change_signal_results_in_hardware_write(
    settings_manager,
):
    settings_manager.brightness = 128

    brightness_path = Path("/sys/class/backlight/test/brightness")

    with (
        patch.object(
            HardwareManager,
            "_find_brightness_device",
            return_value=brightness_path,
        ),
        patch.object(
            HardwareManager,
            "_read_max_brightness",
            return_value=100,
        ),
        patch.object(
            HardwareManager,
            "_write_brightness",
            return_value=True,
        ) as write_brightness,
    ):
        HardwareManager(settings_manager)

        # HardwareManager.__init__() applies the initial brightness.
        # Ignore that write because this test is specifically checking
        # the brightnessChanged callback.
        write_brightness.reset_mock()

        callback = settings_manager.brightnessChanged.connect.call_args.args[0]

        settings_manager.brightness = 200

        callback()

    write_brightness.assert_called_once_with(
        brightness_path,
        78,
    )
