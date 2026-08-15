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

    Text {
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.05

        anchors.horizontalCenter: parent.horizontalCenter

        text: "Shift Light Settings"

        color: Theme.font1

        font.pixelSize: 28
        font.bold: true
    }

    // ===============================================================
    // ENABLED
    // ===============================================================

    Text {
        x: parent.width * 0.20
        y: parent.height * 0.20

        text: "Shift lights"

        color: Theme.font1

        font.pixelSize: 22
    }

    Rectangle {
        x: parent.width * 0.60
        y: parent.height * 0.16

        width: parent.width * 0.10
        height: parent.height * 0.10

        color: settings.shiftLightsEnabled
               ? ColorPalette.softGreen
               : ColorPalette.crimson

        radius: 4

        Text {
            anchors.centerIn: parent

            text: settings.shiftLightsEnabled
                  ? "On"
                  : "Off"

            color: ColorPalette.black

            font.pixelSize: 18
            font.bold: true
        }

        MouseArea {
            anchors.fill: parent

            onClicked: {
                settings.shiftLightsEnabled =
                    !settings.shiftLightsEnabled
            }
        }
    }

    // ===============================================================
    // COLOR 1
    // ===============================================================

    Text {
        x: parent.width * 0.20
        y: parent.height * 0.34

        text: "Shift Light Color 1"

        color: Theme.font1

        font.pixelSize: 20
    }

    ColorSelector {
        x: parent.width * 0.50
        y: parent.height * 0.29

        width: parent.width * 0.30
        height: parent.height * 0.10

        colorIndex: Number(settings.shiftLightColor1)

        onChanged: function(index) {
            settings.shiftLightColor1 = index
        }
    }

    // ===============================================================
    // COLOR 2
    // ===============================================================

    Text {
        x: parent.width * 0.20
        y: parent.height * 0.46

        text: "Shift Light Color 2"

        color: Theme.font1

        font.pixelSize: 20
    }

    ColorSelector {
        x: parent.width * 0.50
        y: parent.height * 0.41

        width: parent.width * 0.30
        height: parent.height * 0.10

        colorIndex: Number(settings.shiftLightColor2)

        onChanged: function(index) {
            settings.shiftLightColor2 = index
        }
    }

    // ===============================================================
    // COLOR 3
    // ===============================================================

    Text {
        x: parent.width * 0.20
        y: parent.height * 0.58

        text: "Shift Light Color 3"

        color: Theme.font1

        font.pixelSize: 20
    }

    ColorSelector {
        x: parent.width * 0.50
        y: parent.height * 0.53

        width: parent.width * 0.30
        height: parent.height * 0.10

        colorIndex: Number(settings.shiftLightColor3)

        onChanged: function(index) {
            settings.shiftLightColor3 = index
        }
    }

    // ===============================================================
    // COLOR 4
    // ===============================================================

    Text {
        x: parent.width * 0.20
        y: parent.height * 0.70

        text: "Shift Light Color 4"

        color: Theme.font1

        font.pixelSize: 20
    }

    ColorSelector {
        x: parent.width * 0.50
        y: parent.height * 0.65

        width: parent.width * 0.30
        height: parent.height * 0.10

        colorIndex: Number(settings.shiftLightColor4)

        onChanged: function(index) {
            settings.shiftLightColor4 = index
        }
    }

    // ===============================================================
    // STARTING RPM
    // ===============================================================

    Text {
        x: parent.width * 0.20
        y: parent.height * 0.84

        text: "Shift Starting RPM"

        color: Theme.font1

        font.pixelSize: 20
    }

    Text {
        x: parent.width * 0.50
        y: parent.height * 0.84

        width: parent.width * 0.30

        horizontalAlignment: Text.AlignHCenter

        text: Math.max(
            settings.rpmMin,
            settings.rpmShift
            - (14 * settings.shiftLightPadding)
        )

        color: Theme.font1

        font.pixelSize: 20
        font.bold: true
    }

    // ===============================================================
    // PADDING CONTROLS
    // ===============================================================

    Text {
        x: parent.width * 0.20
        y: parent.height * 0.90

        text: "Light Spacing"

        color: Theme.font2

        font.pixelSize: 16
    }

    // ===============================================================
    // DECREASE PADDING
    // ===============================================================

    Rectangle {
        x: parent.width * 0.50
        y: parent.height * 0.89

        width: parent.width * 0.10
        height: parent.height * 0.08

        color: ColorPalette.crimson

        radius: 4

        Text {
            anchors.centerIn: parent

            text: "-"

            color: ColorPalette.black

            font.pixelSize: 28
            font.bold: true
        }

        MouseArea {
            anchors.fill: parent

            onClicked: {
                settings.shiftLightPadding =
                    Math.max(
                        10,
                        settings.shiftLightPadding - 10
                    )
            }
        }
    }

    // ===============================================================
    // CURRENT PADDING
    // ===============================================================

    Text {
        x: parent.width * 0.61
        y: parent.height * 0.90

        width: parent.width * 0.08

        horizontalAlignment: Text.AlignHCenter

        text: settings.shiftLightPadding

        color: Theme.font1

        font.pixelSize: 18
        font.bold: true
    }

    // ===============================================================
    // INCREASE PADDING
    // ===============================================================

    Rectangle {
        x: parent.width * 0.70
        y: parent.height * 0.89

        width: parent.width * 0.10
        height: parent.height * 0.08

        color: ColorPalette.softGreen

        radius: 4

        Text {
            anchors.centerIn: parent

            text: "+"

            color: ColorPalette.black

            font.pixelSize: 28
            font.bold: true
        }

        MouseArea {
            anchors.fill: parent

            onClicked: {
                settings.shiftLightPadding =
                    Math.min(
                        1000,
                        settings.shiftLightPadding + 10
                    )
            }
        }
    }

    // ===============================================================
    // PAGE INDICATORS
    // ===============================================================

    PageIndicator {
        anchors.horizontalCenter: parent.horizontalCenter

        anchors.bottom: parent.bottom
        anchors.bottomMargin: 8

        pageCount: root.pageCount
        currentPage: root.pageIndex
    }
}