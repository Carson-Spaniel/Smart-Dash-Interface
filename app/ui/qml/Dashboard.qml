import QtQuick
import "components"
import QtQuick.Shapes
import Qt5Compat.GraphicalEffects

Item {
    id: root

    // ===============================================================
    // Dashboard Settings
    // ===============================================================

    property bool optimize: false
    property bool shiftLightsEnabled: true

    // ===============================================================
    // Background
    // ===============================================================

    Rectangle {
        id: screenBackground

        anchors.fill: parent
        color: Theme.background2
    }

    property real panelCutoutGap: 30
    property real edgePadding: 30



    // ===============================================================
    // RPM BAR
    // ===============================================================

 

    Rectangle {
        id: rpmBar

        anchors.left: parent.left
        anchors.top: parent.top

        height: parent.height * .3

        width: {
            var rpm = Number(vehicle.rpm)

            if (!isFinite(rpm) || rpm < 0)
                return 0

            if (settingsManager.rpmMax <= 0)
                return 0

            return parent.width
                   * Math.min(
                       1.0,
                       rpm / settingsManager.rpmMax
                   )
        }

        color: {
            var rpm = Number(vehicle.rpm)

            if (!isFinite(rpm))
                return ColorPalette.success

            return rpm < settingsManager.rpmShift
                   ? ColorPalette.success
                   : ColorPalette.danger
        }

        Behavior on width {
            NumberAnimation {
                duration: 80
            }
        }
    }


    // ===============================================================
    // SHIFT MARKER
    // ===============================================================

    Rectangle {
        id: shiftMarker

        x: {
            if (settingsManager.rpmMax <= 0)
                return 0

            return parent.width
                   * Math.min(
                       1.0,
                       settingsManager.rpmShift
                       / settingsManager.rpmMax
                   )
        }

        y: 0

        width: 4

        height: parent.height * 0.2

        color: ColorPalette.danger
    }


    // ===============================================================
    // FUEL
    // ===============================================================

    Rectangle {
        anchors.left: parent.left
        anchors.bottom: parent.bottom

        height: parent.height * 0.5
        width: parent.width * 0.18

        color: Theme.background1
    }

    Item {
        id: fuelContainer

        anchors.left: parent.left
        anchors.right: parent.right

        anchors.leftMargin: parent.width * 0.18
        anchors.rightMargin: edgePadding

        anchors.bottom: parent.bottom

        height: parent.height * 0.30




        // -----------------------------------------------------------
        // Fuel Level
        // -----------------------------------------------------------

        Rectangle {
            id: fuelLevel

            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom

            width: {
                var fuel = Number(vehicle.fuelLevel)

                if (!isFinite(fuel))
                    return 0

                return parent.width * Math.max(
                    0,
                    Math.min(1, fuel / 100)
                )
            }

            color: {
                var fuel = Number(vehicle.fuelLevel)

                if (!isFinite(fuel))
                    return ColorPalette.inactive

                if (fuel > 75)
                    return ColorPalette.success

                if (fuel > 50)
                    return ColorPalette.warning

                if (fuel > 30)
                    return ColorPalette.orange

                return ColorPalette.danger
            }

            Behavior on width {
                NumberAnimation {
                    duration: 200
                }
            }
        }
    }



    // ===============================================================
    // MAIN BACKGROUND
    // ===============================================================

    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter

        height: parent.height * 0.5

        color: Theme.background1
    }


    // ===============================================================
    // MAIN PANEL
    // ===============================================================

    Rectangle {
        id: mainPanel

        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter

        width: parent.width * 0.87
        height: parent.height * 0.81

        radius: 150

        color: Theme.background1

        // border.width: 2
        // border.color: ColorPalette.border
    }


    // ===============================================================
    // RPM
    // ===============================================================

    Text {
        anchors.horizontalCenter: parent.horizontalCenter

        anchors.verticalCenter: parent.verticalCenter
        anchors.verticalCenterOffset: -20

        width: parent.width * 0.60

        horizontalAlignment: Text.AlignHCenter

        text: {
            var rpm = Number(vehicle.rpm)

            if (!isFinite(rpm))
                return "----"

            return Math.round(rpm)
                   .toString()
                   .padStart(4, " ")
        }

        color: Theme.font1

        font.pixelSize: 250

        font.bold: true
    }


    // ===============================================================
    // RPM LABEL
    // ===============================================================

    Text {
        anchors.horizontalCenter: parent.horizontalCenter

        y: parent.height * 0.62

        text: "RPM"

        color: Theme.font2

        font.pixelSize: 30
    }


    // ===============================================================
    // MPG
    // ===============================================================

    Column {
        anchors.left: parent.left
        anchors.leftMargin: parent.width * 0.05

        anchors.verticalCenter: parent.verticalCenter

        width: parent.width * 0.20

        spacing: 4

        Text {
            width: parent.width

            horizontalAlignment: Text.AlignHCenter

            text: {
                if (root.optimize)
                    return "--"

                var mpg = Number(vehicle.mpg)

                if (!isFinite(mpg))
                    return "--"

                return mpg.toFixed(1)
            }

            color: Theme.font1

            font.pixelSize: 100
            font.bold: true
        }

        Text {
            width: parent.width

            horizontalAlignment: Text.AlignHCenter

            text: "MPG"

            color: Theme.font2

            font.pixelSize: 30
        }
    }


    // ===============================================================
    // SPEED
    // ===============================================================

    Column {
        anchors.right: parent.right
        anchors.rightMargin: parent.width * 0.05

        anchors.verticalCenter: parent.verticalCenter

        width: parent.width * 0.20

        spacing: 4

        Text {
            width: parent.width

            horizontalAlignment: Text.AlignHCenter

            text: {
                if (root.optimize)
                    return "--"

                var speed = Number(vehicle.speed)

                if (!isFinite(speed))
                    return "--"

                return speed.toFixed(0)
            }

            color: Theme.font1

            font.pixelSize: 100
            font.bold: true
        }

        Text {
            width: parent.width

            horizontalAlignment: Text.AlignHCenter

            text: "MPH"

            color: Theme.font2

            font.pixelSize: 30
        }
    }


    // ===============================================================
    // VOLTAGE
    // ===============================================================

    Text {
        anchors.left: parent.left
        anchors.leftMargin: parent.width * 0.25

        anchors.bottom: parent.bottom
        anchors.bottomMargin: parent.height * 0.11

        text: {
            var voltage = Number(vehicle.voltage)

            if (!isFinite(voltage))
                return "--"

            return voltage.toFixed(1) + " V"
        }

        color: Theme.font1

        font.pixelSize: 50
    }


    // ===============================================================
    // TEMPERATURE
    // ===============================================================

    Text {
        anchors.right: parent.right
        anchors.rightMargin: parent.width * 0.25

        anchors.bottom: parent.bottom
        anchors.bottomMargin: parent.height * 0.11

        text: {
            var temperature =
                Number(vehicle.airTemperature)

            if (!isFinite(temperature))
                return "--"

            return temperature.toFixed(1) + "°F"
        }

        color: Theme.font1

        font.pixelSize: 50
    }


    // ===============================================================
    // SHIFT LIGHTS
    // ===============================================================

    ShiftLights {
        anchors.horizontalCenter: parent.horizontalCenter

        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.14

        width: parent.width * 0.80
        height: 100

        visible: settingsManager.shiftLightsEnabled

        // -----------------------------------------------------------
        // Vehicle RPM
        // -----------------------------------------------------------

        rpm: Number(vehicle.rpm)

        // -----------------------------------------------------------
        // RPM Settings
        // -----------------------------------------------------------

        shiftRpm:
            Number(settingsManager.rpmShift)

        maximumRpm:
            Number(settingsManager.rpmMax)

        // -----------------------------------------------------------
        // Shift Light Settings
        // -----------------------------------------------------------

        padding:
            Number(
                settingsManager.shiftLightPadding
            )

        // -----------------------------------------------------------
        // Color Indexes
        // -----------------------------------------------------------

        color1Index:
            Number(settingsManager.shiftLightColor1)

        color2Index:
            Number(settingsManager.shiftLightColor2)

        color3Index:
            Number(settingsManager.shiftLightColor3)

        color4Index:
            Number(settingsManager.shiftLightColor4)
    }


    // ===============================================================
    // INVERSE MAIN PANEL CUTOUT
    // ===============================================================

    Item {
        id: inversePanel

        anchors.fill: parent


        // -----------------------------------------------------------
        // TOP
        // -----------------------------------------------------------

        Rectangle {
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right

            height: root.edgePadding

            color: Theme.background1
        }


        // -----------------------------------------------------------
        // BOTTOM
        // -----------------------------------------------------------

        Rectangle {
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right

            height: root.edgePadding

            color: Theme.background1
        }


        // -----------------------------------------------------------
        // LEFT
        // -----------------------------------------------------------

        Rectangle {
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom

            width: root.edgePadding

            color: Theme.background1
        }


        // -----------------------------------------------------------
        // RIGHT
        // -----------------------------------------------------------

        Rectangle {
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom

            width: root.edgePadding

            color: Theme.background1
        }


        // -----------------------------------------------------------
        // CUTOUT MASK
        // -----------------------------------------------------------

        Rectangle {
            id: mainPanelCutout

            anchors.centerIn: parent

            width: mainPanel.width
                   + (root.panelCutoutGap * 2)

            height: mainPanel.height
                    + (root.panelCutoutGap * 2)

            radius: mainPanel.radius
                    + root.panelCutoutGap

            color: "white"

            visible: false
        }


        // -----------------------------------------------------------
        // INVERSE OVERLAY
        // -----------------------------------------------------------

        Rectangle {
            id: inverseOverlay

            anchors.fill: parent

            anchors.margins: root.edgePadding

            color: Theme.background1

            layer.enabled: true

            layer.effect: OpacityMask {
                maskSource: mainPanelCutout
                invert: true
            }
        }
    }

    // ===============================================================
    // FUEL TEXT
    // ===============================================================

    Text {
        anchors.left: parent.left
        anchors.leftMargin: parent.width * 0.04

        anchors.bottom: parent.bottom
        anchors.bottomMargin: parent.height * 0.032

        text: {
            var fuel = Number(vehicle.fuelLevel)

            if (!isFinite(fuel))
                return "--"

            return fuel.toFixed(1) + "%"
        }

        color: Theme.font1

        font.pixelSize: 50
        font.bold: true
    }
}