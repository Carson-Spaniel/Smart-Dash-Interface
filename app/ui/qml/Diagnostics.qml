import QtQuick
import "components"

Item {
    id: root

    property int pageCount: 1
    property int pageIndex: 1
    property bool clearing: false
    property bool cleared: false

    Rectangle {
        anchors.fill: parent
        color: Theme.background1
    }

    TitleItem {
        title: "Trouble Codes"
    }

    // ===============================================================
    // No codes
    // ===============================================================

    Text {
        anchors.horizontalCenter: parent.horizontalCenter

        y: parent.height * 0.25

        visible: !root.clearing

        text: root.cleared
              ? "Trouble codes have been cleared."
              : "No trouble codes detected."

        color: Theme.font1

        font.pixelSize: 24
    }

    // ===============================================================
    // Clear button
    // ===============================================================

    Rectangle {
        anchors.horizontalCenter: parent.horizontalCenter

        anchors.bottom: parent.bottom
        anchors.bottomMargin: parent.height * 0.10

        width: parent.width * 0.12
        height: parent.height * 0.10

        radius: 10

        color: root.clearing
               ? "#303030"
               : ColorPalette.crimson

        visible: !root.cleared

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

            onClicked: {
                if (!root.clearing) {
                    root.clearing = true

                    // The actual DiagnosticsService will
                    // eventually perform the OBD operation.
                }
            }
        }
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter

        anchors.bottom: parent.bottom
        anchors.bottomMargin: parent.height * 0.10

        visible: root.clearing

        text: "Turn off the engine before clearing codes!"

        color: Theme.font1

        font.pixelSize: 18
    }

    // ===============================================================
    // PAGE INDICATORS
    // ===============================================================

    PageIndicator {
        pageCount: root.pageCount
        currentPage: root.pageIndex
    }
}