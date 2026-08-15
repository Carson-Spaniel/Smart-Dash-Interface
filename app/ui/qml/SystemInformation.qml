import QtQuick
import "components"

Item {
    id: root

    property int pageCount: 1
    property int pageIndex: 1
    property string version: "0.1.0"
    property bool wifiConnected: false
    property bool developmentMode: false

    Rectangle {
        anchors.fill: parent

        color: "#101010"
    }

    Text {
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.05

        anchors.horizontalCenter: parent.horizontalCenter

        text: "System Information"

        color: "white"

        font.pixelSize: 28
        font.bold: true
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter

        y: parent.height * 0.15

        text: "Version: " + root.version

        color: "#dddddd"

        font.pixelSize: 20
    }

    Text {
        x: parent.width * 0.20
        y: parent.height * 0.25

        text: "System Updates"

        color: "white"

        font.pixelSize: 22
    }

    Rectangle {
        x: parent.width * 0.60
        y: parent.height * 0.20

        width: parent.width * 0.20
        height: parent.height * 0.10

        color: root.wifiConnected
               ? "#00d26a"
               : "#ff3030"

        Text {
            anchors.centerIn: parent

            text: root.wifiConnected
                  ? "Update"
                  : "No Wifi"

            color: "black"

            font.pixelSize: 18
        }
    }

    Text {
        x: parent.width * 0.20
        y: parent.height * 0.37

        text: "Development Mode"

        color: "white"

        font.pixelSize: 22
    }

    Rectangle {
        x: parent.width * 0.60
        y: parent.height * 0.32

        width: parent.width * 0.10
        height: parent.height * 0.10

        color: root.developmentMode
               ? "#00d26a"
               : "#ff3030"

        Text {
            anchors.centerIn: parent

            text: root.developmentMode
                  ? "On"
                  : "Off"

            color: "black"

            font.pixelSize: 18
        }

        MouseArea {
            anchors.fill: parent

            onClicked: {
                root.developmentMode =
                    !root.developmentMode
            }
        }
    }

    Rectangle {
        anchors.horizontalCenter: parent.horizontalCenter

        anchors.bottom: parent.bottom
        anchors.bottomMargin: parent.height * 0.10

        width: parent.width * 0.10
        height: parent.height * 0.10

        color: "#ff3030"

        Text {
            anchors.centerIn: parent

            text: "Exit"

            color: "black"

            font.pixelSize: 18
        }

        MouseArea {
            anchors.fill: parent

            onClicked: {
                Qt.quit()
            }
        }
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

        font.pixelSize: 14
        font.bold: true
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