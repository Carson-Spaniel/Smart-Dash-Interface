import QtQuick
import "components"

Item {
    id: root

    property int brightness: 255
    property bool optimize: false
    property bool delayedReadings: false
    property int pageCount: 1
    property int pageIndex: 1

    Rectangle {
        anchors.fill: parent
        color: "#101010"
    }

    Text {
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.05

        anchors.horizontalCenter: parent.horizontalCenter

        text: "General Settings"

        color: Theme.font1

        font.pixelSize: 28
        font.bold: true
    }

    // ===============================================================
    // Brightness
    // ===============================================================

    Text {
        x: parent.width * 0.20
        y: parent.height * 0.25

        text: "Brightness"

        color: Theme.font1

        font.pixelSize: 22
    }

    Text {
        x: parent.width * 0.65
        y: parent.height * 0.25

        text: Math.round(
            root.brightness / 255 * 100
        ) + "%"

        color: Theme.font1

        font.pixelSize: 22
    }

    Rectangle {
        x: parent.width * 0.50
        y: parent.height * 0.20

        width: parent.width * 0.10
        height: parent.height * 0.10

        color: "#ff3030"

        Text {
            anchors.centerIn: parent

            text: "-"

            color: "black"

            font.pixelSize: 30
        }

        MouseArea {
            anchors.fill: parent

            onClicked: {
                root.brightness = Math.max(
                    0,
                    root.brightness - 15
                )
            }
        }
    }

    Rectangle {
        x: parent.width * 0.70
        y: parent.height * 0.20

        width: parent.width * 0.10
        height: parent.height * 0.10

        color: "#00d26a"

        Text {
            anchors.centerIn: parent

            text: "+"

            color: "black"

            font.pixelSize: 30
        }

        MouseArea {
            anchors.fill: parent

            onClicked: {
                root.brightness = Math.min(
                    255,
                    root.brightness + 15
                )
            }
        }
    }

    // ===============================================================
    // Optimize
    // ===============================================================

    Text {
        x: parent.width * 0.20
        y: parent.height * 0.37

        text: "Optimize readings"

        color: Theme.font1

        font.pixelSize: 22
    }

    Rectangle {
        x: parent.width * 0.60
        y: parent.height * 0.32

        width: parent.width * 0.10
        height: parent.height * 0.10

        color: root.optimize
               ? "#00d26a"
               : "#ff3030"

        Text {
            anchors.centerIn: parent

            text: root.optimize
                  ? "On"
                  : "Off"

            color: "black"

            font.pixelSize: 18
        }

        MouseArea {
            anchors.fill: parent

            onClicked: {
                root.optimize = !root.optimize
            }
        }
    }

    // ===============================================================
    // Delay
    // ===============================================================

    Text {
        x: parent.width * 0.20
        y: parent.height * 0.49

        text: "Delay readings"

        color: Theme.font1

        font.pixelSize: 22
    }

    Rectangle {
        x: parent.width * 0.60
        y: parent.height * 0.44

        width: parent.width * 0.10
        height: parent.height * 0.10

        color: root.delayedReadings
               ? "#00d26a"
               : "#ff3030"

        Text {
            anchors.centerIn: parent

            text: root.delayedReadings
                  ? "On"
                  : "Off"

            color: "black"

            font.pixelSize: 18
        }

        MouseArea {
            anchors.fill: parent

            onClicked: {
                root.delayedReadings =
                    !root.delayedReadings
            }
        }
    }

    // ===============================================================
    // Reset Performance
    // ===============================================================

    Text {
        x: parent.width * 0.20
        y: parent.height * 0.61

        text: "Reset Performance Stats"

        color: Theme.font1

        font.pixelSize: 22
    }

    Rectangle {
        x: parent.width * 0.60
        y: parent.height * 0.56

        width: parent.width * 0.10
        height: parent.height * 0.10

        color: "#00d26a"

        Text {
            anchors.centerIn: parent

            text: "Reset"

            color: "black"

            font.pixelSize: 18
        }

        MouseArea {
            anchors.fill: parent

            onClicked: {
                // Connect this to TripService later.
                console.log("Reset performance")
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