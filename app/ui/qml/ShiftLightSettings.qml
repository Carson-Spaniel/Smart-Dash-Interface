import QtQuick
import "components"

Item {
    id: root

    property var settings: settingsManager
    property int pageCount: 1
    property int pageIndex: 1

    Rectangle {
        anchors.fill: parent

        color: Theme.background1
    }

    // ===============================================================
    // TITLE
    // ===============================================================

    TitleItem {
        title: "Shift Light Settings"
    }

    // ===============================================================
    // ENABLED
    // ===============================================================

    ToggleButtonLineItem {
        y: parent.height * .1
        label: "Shift Lights"

        valueText: settings.shiftLightsEnabled
                  ? "On"
                  : "Off"

        buttonColor: settings.shiftLightsEnabled
               ? ColorPalette.softGreen
               : ColorPalette.crimson

        onToggleButtonClicked: {
                settings.shiftLightsEnabled =
                    !settings.shiftLightsEnabled
            }
    }

    // ===============================================================
    // COLOR 1
    // ===============================================================

    ColorPickerLineItem {
        label: "Shift Light Color 1"
        y: parent.height * .2
        colorIndex: Number(settings.shiftLightColor1)
        onColorChanged: function(index) {
            settings.shiftLightColor1 = index
        }
    }

    // ===============================================================
    // COLOR 2
    // ===============================================================

    ColorPickerLineItem {
        label: "Shift Light Color 2"
        y: parent.height * .3
        colorIndex: Number(settings.shiftLightColor2)
        onColorChanged: function(index) {
            settings.shiftLightColor2 = index
        }
    }

    // ===============================================================
    // COLOR 3
    // ===============================================================

    ColorPickerLineItem {
        label: "Shift Light Color 3"
        y: parent.height * .4
        colorIndex: Number(settings.shiftLightColor3)
        onColorChanged: function(index) {
            settings.shiftLightColor3 = index
        }
    }

    // ===============================================================
    // COLOR 4
    // ===============================================================

    ColorPickerLineItem {
        label: "Shift Light Color 4"
        y: parent.height * .5
        colorIndex: Number(settings.shiftLightColor4)
        onColorChanged: function(index) {
            settings.shiftLightColor4 = index
        }
    }

    // ===============================================================
    // STARTING RPM
    // ===============================================================

    PlusMinusLineItem {
        label: "Shift Starting RPM"
        y: parent.height * .6
        valueText: Math.max(
            settings.rpmMin,
            settings.rpmShift
            - (14 * settings.shiftLightPadding)
        )
        onLeftClicked: {
                settings.shiftLightPadding =
                    Math.min(
                        1000,
                        settings.shiftLightPadding + 10
                    )
            }
        onRightClicked: {
                settings.shiftLightPadding =
                    Math.max(
                        10,
                        settings.shiftLightPadding - 10
                    )
            }
    }

    // ===============================================================
    // PAGE INDICATORS
    // ===============================================================

    PageIndicator {
        pageCount: root.pageCount
        currentPage: root.pageIndex
    }
}