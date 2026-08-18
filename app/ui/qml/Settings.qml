import QtQuick
import "components"

Item {
    id: root

    property int brightness: 255
    property bool optimize: false
    property bool delayedReadings: false
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
            root.brightness / 255 * 100
        ) + "%"
        onLeftClicked: {
            root.brightness = Math.max(
                0,
                root.brightness - 15
            )
        }
        onRightClicked: {
            root.brightness = Math.min(
                255,
                root.brightness + 15
            )
        }
    }

    // ===============================================================
    // Optimize
    // ===============================================================

    ToggleButtonLineItem {
        y: parent.height * .2
        label: "Optimize readings"
        valueText: root.optimize
                  ? "On"
                  : "Off"
        buttonColor: root.optimize
               ? ColorPalette.softGreen
               : ColorPalette.crimson
        onToggleButtonClicked: {
                root.optimize = !root.optimize
            }
    }

    // ===============================================================
    // Delay
    // ===============================================================

    ToggleButtonLineItem {
        y: parent.height * .3
        label: "Delay readings"
        valueText: root.delayedReadings
                  ? "On"
                  : "Off"
        buttonColor: root.delayedReadings
               ? ColorPalette.softGreen
               : ColorPalette.crimson
        onToggleButtonClicked: {
                root.delayedReadings =
                    !root.delayedReadings
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