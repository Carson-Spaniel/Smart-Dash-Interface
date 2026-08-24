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

    TitleItem {
        title: "RPM Settings"
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

    // ================================================================
    // Maximum RPM
    // ================================================================

    Column {
        id: maxRpmText

        anchors.left: parent.left
        anchors.leftMargin: parent.width * 0.05

        anchors.verticalCenter: parent.verticalCenter

        width: parent.width * 0.20

        spacing: 4

        Text {
            width: parent.width

            horizontalAlignment: Text.AlignHCenter

            text: settings.rpmMax

            color: Theme.font1

            font.pixelSize: 100
            font.bold: true
        }

        Text {
            width: parent.width

            horizontalAlignment: Text.AlignHCenter

            text: "MAX"

            color: Theme.font2

            font.pixelSize: 30
        }
    }

    // ================================================================
    // Shift RPM
    // ================================================================

    Column {
        id: shiftPointText

        anchors.right: parent.right
        anchors.rightMargin: parent.width * 0.05

        anchors.verticalCenter: parent.verticalCenter

        width: parent.width * 0.20

        spacing: 4

        Text {
            width: parent.width

            horizontalAlignment: Text.AlignHCenter

            text: settings.rpmShift

            color: Theme.font1

            font.pixelSize: 100
            font.bold: true
        }

        Text {
            width: parent.width

            horizontalAlignment: Text.AlignHCenter

            text: "SHIFT"

            color: Theme.font2

            font.pixelSize: 30
        }
    }

    // ================================================================
    // Maximum RPM +
    // ================================================================

    ButtonItem {
        buttonText: "+"
        color: ColorPalette.softGreen
        onButtonClicked: {
                settings.rpmMax = Math.min(
                    12000,
                    settings.rpmMax + 100
                )
            }
        x: (maxRpmText.x) + (maxRpmText.width/2) - (width / 2)
        y: parent.height * 0.25

        height: parent.height * .1
    }

    // ================================================================
    // Maximum RPM -
    // ================================================================

    ButtonItem {
        buttonText: "-"
        color: ColorPalette.crimson
        onButtonClicked: {
                settings.rpmMax = Math.max(
                    1000,
                    settings.rpmMax - 100
                )
            }
        x: (maxRpmText.x) + (maxRpmText.width/2) - (width / 2)
        y: parent.height * 0.75 - height

        height: parent.height * .1
    }

    // ================================================================
    // Shift RPM +
    // ================================================================

    ButtonItem {
        buttonText: "+"
        color: ColorPalette.softGreen
        onButtonClicked: {
                settings.rpmShift = Math.min(
                    settings.rpmMax,
                    settings.rpmShift + 100
                )
            }
        x: (shiftPointText.x) + (shiftPointText.width/2) - (width / 2)
        y: parent.height * 0.25

        height: parent.height * .1
    }

    // ================================================================
    // Shift RPM -
    // ================================================================

    ButtonItem {
        buttonText: "-"
        color: ColorPalette.crimson
        onButtonClicked: {
                settings.rpmShift = Math.max(
                    1000,
                    settings.rpmShift - 100
                )
            }
        x: (shiftPointText.x) + (shiftPointText.width/2) - (width / 2)
        y: parent.height * 0.75 - height

        height: parent.height * .1
    }

    // ===============================================================
    // PAGE INDICATORS
    // ===============================================================

    PageIndicator {
        pageCount: root.pageCount
        currentPage: root.pageIndex
    }
}