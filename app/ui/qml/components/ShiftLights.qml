import QtQuick
import ".."

Item {
    id: root

    // ===============================================================
    // Inputs
    // ===============================================================

    property real rpm: 0

    property real shiftRpm: 6500

    property real maximumRpm: 8000

    property real padding: 1000

    // ===============================================================
    // Color Selection
    // ===============================================================
    //
    // These are indexes into ColorPalette.colors.
    //
    // Dashboard.qml supplies these from SettingsManager.
    //

    property int color1Index: 12
    property int color2Index: 8
    property int color3Index: 5
    property int color4Index: 0

    // ===============================================================
    // Palette
    // ===============================================================

    function paletteColor(index, fallback) {
        if (!ColorPalette.colors)
            return fallback

        if (index < 0)
            return fallback

        if (index >= ColorPalette.colors.length)
            return fallback

        var selectedColor = ColorPalette.colors[index]

        if (selectedColor === undefined)
            return fallback

        return selectedColor
    }

    // ===============================================================
    // Resolved Shift Light Colors
    // ===============================================================

    readonly property color color1:
        paletteColor(
            color1Index,
            ColorPalette.green
        )

    readonly property color color2:
        paletteColor(
            color2Index,
            ColorPalette.yellow
        )

    readonly property color color3:
        paletteColor(
            color3Index,
            ColorPalette.orange
        )

    readonly property color color4:
        paletteColor(
            color4Index,
            ColorPalette.red
        )

    // ===============================================================
    // Blink State
    // ===============================================================

    property bool blinking: false

    Timer {
        id: blinkTimer

        interval: 100

        repeat: true

        running: root.rpm >= root.shiftRpm

        onTriggered: {
            root.blinking = !root.blinking
        }
    }

    // ===============================================================
    // Reset Blinking
    // ===============================================================

    onRpmChanged: {
        if (root.rpm < root.shiftRpm) {
            root.blinking = false
        }
    }

    onShiftRpmChanged: {
        if (root.rpm < root.shiftRpm) {
            root.blinking = false
        }
    }

    // ===============================================================
    // Lights
    // ===============================================================

    Row {
        anchors.fill: parent

        spacing: width * 0.015

        Repeater {
            model: 12

            delegate: Item {
                id: light

                required property int index

                width: (
                    parent.width
                    - parent.spacing * 11
                ) / 12

                height: parent.height

                // ===================================================
                // Light Color
                // ===================================================

                property color lightColor: {
                    if (index < 4) {
                        return root.color1
                    }

                    if (index < 8) {
                        return root.color2
                    }

                    return root.color3
                }

                // ===================================================
                // Start RPM
                // ===================================================

                property real startRpm:
                    Math.max(
                        0,
                        root.shiftRpm - (14 * root.padding)
                    )

                // ===================================================
                // Trigger RPM
                // ===================================================

                property real triggerRpm: {
                    var range =
                        root.shiftRpm
                        - startRpm

                    if (range <= 0) {
                        return root.shiftRpm
                    }

                    return startRpm
                           + (
                               range
                               * (index + 1)
                               / 14
                           )
                }

                // ===================================================
                // Active
                // ===================================================

                property bool active:
                    root.rpm >= triggerRpm

                // ===================================================
                // Light
                // ===================================================

                Rectangle {
                    anchors.centerIn: parent

                    width: Math.min(
                        parent.width,
                        parent.height
                    )

                    height: width

                    radius: width / 2

                    // =================================================
                    // Color
                    // =================================================

                    color: {
                        // ---------------------------------------------
                        // Shift RPM reached.
                        //
                        // All lights blink using color 4.
                        // ---------------------------------------------

                        if (root.rpm >= root.shiftRpm) {
                            if (root.blinking) {
                                return root.color4
                            }

                            return Theme.background1
                        }

                        // ---------------------------------------------
                        // Below shift RPM.
                        //
                        // Progressively illuminate lights.
                        // ---------------------------------------------

                        if (light.active) {
                            return light.lightColor
                        }

                        return Theme.background1
                    }

                    // =================================================
                    // Border
                    // =================================================

                    border.width: 3

                    border.color:
                        light.active
                        ? "transparent"
                        : ColorPalette.lightGray

                    // =================================================
                    // Animation
                    // =================================================

                    Behavior on color {
                        ColorAnimation {
                            duration: 50
                        }
                    }
                }
            }
        }
    }
}