import QtQuick
import "components"

Item {
    id: root

    property int pageCount: 1
    property int pageIndex: 1
    property string version: "0.1.0"

    Rectangle {
        anchors.fill: parent

        color: Theme.background1
    }

    TitleItem {
        title: "System Information"
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        y: parent.height * 0.09
        text: "Version: " + root.version
        color: Theme.font2
        font.pixelSize: 30
    }

    ButtonItem {
        buttonText: "Exit"
        color: ColorPalette.crimson
        onButtonClicked: {
                Qt.quit()
            }
        height: parent.height * .1
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: parent.height * 0.10
    }

    // ===============================================================
    // CONNECTION
    // ===============================================================

    Text {
        anchors.top: parent.top
        anchors.right: parent.right

        anchors.topMargin: 20
        anchors.rightMargin: 25

        text: vehicle.connected
              ? "CONNECTED"
              : "DISCONNECTED"

        color: vehicle.connected
               ? ColorPalette.success
               : ColorPalette.danger

        font.pixelSize: 30
        font.bold: true
    }

    // ===============================================================
    // PAGE INDICATORS
    // ===============================================================

    PageIndicator {
        pageCount: root.pageCount
        currentPage: root.pageIndex
    }
}