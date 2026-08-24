import QtQuick
import "."

Item {
    id: root

    property int colorIndex: 0

    signal changed(int index)

    // ===============================================================
    // Palette
    // ===============================================================

    readonly property var colors: ColorPalette.colors

    // ===============================================================
    // Selected Color
    // ===============================================================

    Rectangle {
        anchors.fill: parent

        color: {
            if (
                root.colorIndex >= 0 &&
                root.colorIndex < root.colors.length
            ) {
                return root.colors[root.colorIndex]
            }

            return ColorPalette.inactive
        }

        border.width: 2
        border.color: "#555555"

        Text {
            anchors.centerIn: parent

            text: root.colorIndex + 1

            color: "#000000"

            font.pixelSize: 30
            font.bold: true
        }
    }

    // ===============================================================
    // Previous
    // ===============================================================

    Rectangle {
        anchors.left: parent.left
        anchors.verticalCenter: parent.verticalCenter

        width: parent.height
        height: parent.height

        color: "#252525"

        Text {
            anchors.centerIn: parent

            text: "<"

            color: "white"

            font.pixelSize: 28
            font.bold: true
        }

        MouseArea {
            anchors.fill: parent

            onClicked: {
                var next = root.colorIndex - 1

                if (next < 0)
                    next = root.colors.length - 1

                root.colorIndex = next
                root.changed(next)
            }
        }
    }

    // ===============================================================
    // Next
    // ===============================================================

    Rectangle {
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter

        width: parent.height
        height: parent.height

        color: "#252525"

        Text {
            anchors.centerIn: parent

            text: ">"

            color: "white"

            font.pixelSize: 28
            font.bold: true
        }

        MouseArea {
            anchors.fill: parent

            onClicked: {
                var next =
                    (root.colorIndex + 1)
                    % root.colors.length

                root.colorIndex = next
                root.changed(next)
            }
        }
    }
}