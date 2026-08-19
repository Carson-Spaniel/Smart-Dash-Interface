import QtQuick
import "components"

Item {
    id: root

    property int pageCount: 1
    property int pageIndex: 1

    Rectangle {
        anchors.fill: parent
        color: Theme.background1
    }

    TitleItem {
        title: "General Settings"
    }

    // ===============================================================
    // Brightness
    // ===============================================================
    PlusMinusLineItem {
        label: "Brightness"
        valueText: Math.round(
            settings.brightness / 255 * 100
        ) + "%"
        onLeftClicked: {
            settings.brightness =
                Math.max(
                    0,
                    settings.brightness - 15
                )
        }
        onRightClicked: {
            settings.brightness =
                Math.min(
                    255,
                    settings.brightness + 15
                )
        }
    }

    // ===============================================================
    // Optimize
    // ===============================================================

    ToggleButtonLineItem {
        y: parent.height * .2
        label: "Optimize readings"

        valueText: settings.optimizeReadings
                ? "On"
                : "Off"

        buttonColor: settings.optimizeReadings
                    ? ColorPalette.softGreen
                    : ColorPalette.crimson

        onToggleButtonClicked: {
            settings.optimizeReadings =
                !settings.optimizeReadings
        }
    }

    // ===============================================================
    // Delay
    // ===============================================================

    ToggleButtonLineItem {
        y: parent.height * .3
        label: "Delay readings"

        valueText: settings.delayedReadings
                ? "On"
                : "Off"

        buttonColor: settings.delayedReadings
                    ? ColorPalette.softGreen
                    : ColorPalette.crimson

        onToggleButtonClicked: {
            settings.delayedReadings =
                !settings.delayedReadings
        }
    }

    // ===============================================================
    // Reset Performance
    // ===============================================================

    ToggleButtonLineItem {
        y: parent.height * .4
        label: "Reset Performance Stats"
        valueText: "Reset"
        buttonColor: ColorPalette.softGreen
        onToggleButtonClicked: {
                // Connect this to TripService later.
                console.log("Reset performance")
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