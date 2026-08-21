import QtQuick
import "components"

Item {
    id: root

    property int pageCount: 1
    property int pageIndex: 1

    property bool clearing: false

    Rectangle {
        anchors.fill: parent
        color: Theme.background1
    }

    TitleItem {
        title: "Trouble Codes"
    }

    // ===============================================================
    // Stored Trouble Codes
    // ===============================================================

    ListView {
        id: troubleCodeList

        anchors.left: parent.left
        anchors.right: parent.right

        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.18

        anchors.bottom: clearButton.top
        anchors.bottomMargin: parent.height * 0.05

        clip: true

        spacing: 12

        visible: root.troubleCodeCount > 0

        model: vehicle.troubleCodes

        delegate: Rectangle {
            width: troubleCodeList.width * 0.85
            height: 90

            anchors.horizontalCenter: parent.horizontalCenter

            radius: 10

            color: "#252525"

            border.width: 1
            border.color: ColorPalette.crimson

            Column {
                anchors.left: parent.left
                anchors.leftMargin: 20

                anchors.right: parent.right
                anchors.rightMargin: 20

                anchors.verticalCenter: parent.verticalCenter

                spacing: 5

                Text {
                    text: modelData.code

                    color: ColorPalette.crimson

                    font.pixelSize: 24
                    font.bold: true
                }

                Text {
                    width: parent.width

                    text: modelData.description

                    color: Theme.font1

                    font.pixelSize: 16

                    elide: Text.ElideRight
                }
            }
        }
    }

    // ===============================================================
    // No Stored Codes
    // ===============================================================

    Text {
        anchors.horizontalCenter: parent.horizontalCenter

        y: parent.height * 0.30

        visible: root.troubleCodeCount === 0

        text: root.clearing
              ? "Clearing trouble codes..."
              : "No trouble codes detected."

        color: Theme.font1

        font.pixelSize: 24
    }

    // ===============================================================
    // Pending Codes
    // ===============================================================

    Text {
        anchors.horizontalCenter: parent.horizontalCenter

        anchors.bottom: pendingCodeList.top
        anchors.bottomMargin: 8

        visible: root.pendingTroubleCodeCount > 0

        text: "Pending Codes"

        color: Theme.font1

        font.pixelSize: 18
        font.bold: true
    }

    ListView {
        id: pendingCodeList

        anchors.left: parent.left
        anchors.right: parent.right

        anchors.bottom: clearButton.top
        anchors.bottomMargin: parent.height * 0.05

        height: Math.min(
            root.pendingTroubleCodeCount * 70,
            parent.height * 0.25
        )

        clip: true

        spacing: 8

        visible: root.pendingTroubleCodeCount > 0

        model: vehicle.pendingTroubleCodes

        delegate: Rectangle {
            width: pendingCodeList.width * 0.75
            height: 60

            anchors.horizontalCenter: parent.horizontalCenter

            radius: 8

            color: "#202020"

            border.width: 1
            border.color: Theme.font1

            Row {
                anchors.left: parent.left
                anchors.leftMargin: 16

                anchors.right: parent.right
                anchors.rightMargin: 16

                anchors.verticalCenter: parent.verticalCenter

                spacing: 15

                Text {
                    text: modelData.code

                    color: Theme.font1

                    font.pixelSize: 20
                    font.bold: true
                }

                Text {
                    width: pendingCodeList.width * 0.55

                    text: modelData.description

                    color: Theme.font1

                    font.pixelSize: 14

                    elide: Text.ElideRight
                }
            }
        }
    }

    // ===============================================================
    // Clear Button
    // ===============================================================

    Rectangle {
        id: clearButton

        anchors.horizontalCenter: parent.horizontalCenter

        anchors.bottom: parent.bottom
        anchors.bottomMargin: parent.height * 0.10

        width: parent.width * 0.12
        height: parent.height * 0.10

        radius: 10

        visible: root.troubleCodeCount > 0
                 || root.pendingTroubleCodeCount > 0

        color: root.clearing
               ? "#303030"
               : ColorPalette.crimson

        Text {
            anchors.centerIn: parent

            text: root.clearing
                  ? "Clearing..."
                  : "Clear"

            color: "black"

            font.pixelSize: 18
        }

        MouseArea {
            anchors.fill: parent

            enabled: !root.clearing

            onClicked: {
                root.clearing = true

                try {
                    var success = vehicleBackend.clear_trouble_codes()

                    if (success) {
                        root.clearing = false
                    } else {
                        root.clearing = false
                    }
                } catch (error) {
                    console.error(
                        "Failed to clear trouble codes:",
                        error
                    )

                    root.clearing = false
                }
            }
        }
    }

    // ===============================================================
    // Clear Warning
    // ===============================================================

    Text {
        anchors.horizontalCenter: parent.horizontalCenter

        anchors.bottom: clearButton.top
        anchors.bottomMargin: 10

        visible: root.clearing

        text: "Turn off the engine before clearing codes!"

        color: Theme.font1

        font.pixelSize: 18
    }

    // ===============================================================
    // Page Indicators
    // ===============================================================

    PageIndicator {
        pageCount: root.pageCount
        currentPage: root.pageIndex
    }

    // ===============================================================
    // Properties
    // ===============================================================

    property int troubleCodeCount:
        vehicle.troubleCodes
        ? vehicle.troubleCodes.length
        : 0

    property int pendingTroubleCodeCount:
        vehicle.pendingTroubleCodes
        ? vehicle.pendingTroubleCodes.length
        : 0
}