import QtQuick
import "components"

Item {
    id: root

    property int pageCount: 1
    property int pageIndex: 1

    // ================================================================
    // Background
    // ================================================================

    Rectangle {
        anchors.fill: parent

        color: Theme.background1
    }

    // ================================================================
    // Title
    // ================================================================

    Text {
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.05

        anchors.horizontalCenter: parent.horizontalCenter

        text: "RPM Settings"

        color: Theme.font1

        font.pixelSize: 28
        font.bold: true
    }

    // ================================================================
    // Current RPM Label
    // ================================================================

    Text {
        anchors.horizontalCenter: parent.horizontalCenter

        y: parent.height * 0.25

        text: "RPM"

        color: Theme.font2

        font.pixelSize: 24
    }

    // ================================================================
    // Current RPM
    // ================================================================

    Text {
        anchors.horizontalCenter: parent.horizontalCenter

        y: parent.height * 0.40

        text: {
            var rpm = Number(vehicle.rpm)

            if (!isFinite(rpm))
                return "----"

            return Math.round(rpm).toString().padStart(4, " ")
        }

        color: Theme.font1

        font.pixelSize: 72
        font.bold: true
    }

    // ================================================================
    // Maximum RPM
    // ================================================================

    Column {
        anchors.left: parent.left
        anchors.leftMargin: parent.width * 0.20

        y: parent.height * 0.48

        spacing: 8

        Text {
            anchors.horizontalCenter: parent.horizontalCenter

            text: "MAX"

            color: Theme.font2

            font.pixelSize: 18
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter

            text: settings.rpmMax

            color: Theme.font1

            font.pixelSize: 32
        }
    }

    // ================================================================
    // Shift RPM
    // ================================================================

    Column {
        anchors.right: parent.right
        anchors.rightMargin: parent.width * 0.20

        y: parent.height * 0.48

        spacing: 8

        Text {
            anchors.horizontalCenter: parent.horizontalCenter

            text: "SHIFT"

            color: Theme.font2

            font.pixelSize: 18
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter

            text: settings.rpmShift

            color: Theme.font1

            font.pixelSize: 32
        }
    }

    // ================================================================
    // Maximum RPM +
    // ================================================================

    Rectangle {
        x: parent.width * 0.20
        y: parent.height * 0.68

        width: parent.width * 0.10
        height: parent.height * 0.10

        color: ColorPalette.softGreen

        Text {
            anchors.centerIn: parent

            text: "+"

            color: "#000000"

            font.pixelSize: 32
        }

        MouseArea {
            anchors.fill: parent

            onClicked: {
                settings.rpmMax = Math.min(
                    12000,
                    settings.rpmMax + 100
                )
            }
        }
    }

    // ================================================================
    // Maximum RPM -
    // ================================================================

    Rectangle {
        x: parent.width * 0.20
        y: parent.height * 0.82

        width: parent.width * 0.10
        height: parent.height * 0.10

        color: ColorPalette.crimson

        Text {
            anchors.centerIn: parent

            text: "-"

            color: "#000000"

            font.pixelSize: 32
        }

        MouseArea {
            anchors.fill: parent

            onClicked: {
                settings.rpmMax = Math.max(
                    1000,
                    settings.rpmMax - 100
                )
            }
        }
    }

    // ================================================================
    // Shift RPM +
    // ================================================================

    Rectangle {
        x: parent.width * 0.70
        y: parent.height * 0.68

        width: parent.width * 0.10
        height: parent.height * 0.10

        color: ColorPalette.softGreen

        Text {
            anchors.centerIn: parent

            text: "+"

            color: "#000000"

            font.pixelSize: 32
        }

        MouseArea {
            anchors.fill: parent

            onClicked: {
                settings.rpmShift = Math.min(
                    settings.rpmMax,
                    settings.rpmShift + 100
                )
            }
        }
    }

    // ================================================================
    // Shift RPM -
    // ================================================================

    Rectangle {
        x: parent.width * 0.70
        y: parent.height * 0.82

        width: parent.width * 0.10
        height: parent.height * 0.10

        color: ColorPalette.crimson

        Text {
            anchors.centerIn: parent

            text: "-"

            color: "#000000"

            font.pixelSize: 32
        }

        MouseArea {
            anchors.fill: parent

            onClicked: {
                settings.rpmShift = Math.max(
                    1000,
                    settings.rpmShift - 100
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