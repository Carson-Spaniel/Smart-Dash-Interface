import QtQuick

Item {
    id: root

    property bool showFps: false

    Rectangle {
        anchors.fill: parent

        color: "#101010"
    }

    Text {
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.05

        anchors.horizontalCenter: parent.horizontalCenter

        text: "Development Settings"

        color: "white"

        font.pixelSize: 28
        font.bold: true
    }

    Text {
        x: parent.width * 0.20
        y: parent.height * 0.22

        text: "Show FPS"

        color: "white"

        font.pixelSize: 22
    }

    Rectangle {
        x: parent.width * 0.60
        y: parent.height * 0.18

        width: parent.width * 0.10
        height: parent.height * 0.10

        color: root.showFps
               ? "#00d26a"
               : "#ff3030"

        Text {
            anchors.centerIn: parent

            text: root.showFps
                  ? "On"
                  : "Off"

            color: "black"

            font.pixelSize: 18
        }

        MouseArea {
            anchors.fill: parent

            onClicked: {
                root.showFps = !root.showFps
            }
        }
    }

    // Query timing display

    Column {
        x: parent.width * 0.20
        y: parent.height * 0.40

        spacing: 14

        Text {
            text: "RPM Query"
            color: "#aaaaaa"
            font.pixelSize: 18
        }

        Text {
            text: "Speed Query"
            color: "#aaaaaa"
            font.pixelSize: 18
        }

        Text {
            text: "MAF Query"
            color: "#aaaaaa"
            font.pixelSize: 18
        }

        Text {
            text: "Fuel Query"
            color: "#aaaaaa"
            font.pixelSize: 18
        }

        Text {
            text: "Voltage Query"
            color: "#aaaaaa"
            font.pixelSize: 18
        }

        Text {
            text: "Temperature Query"
            color: "#aaaaaa"
            font.pixelSize: 18
        }
    }
}