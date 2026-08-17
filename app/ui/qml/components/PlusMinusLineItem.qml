import QtQuick

Item {
    property alias label: label.text
    property alias valueText: valueText.text
    signal leftClicked()
    signal rightClicked()

    anchors.horizontalCenter: parent.horizontalCenter
    width: parent.width
    height: parent.height * .1
    y: parent.height * .1

    Text {
        id: label
        x: parent.width * 0.20
        anchors.verticalCenter: parent.verticalCenter
        color: Theme.font1
        font.pixelSize: 22
    }

    Rectangle {
        id: leftButton
        x: parent.width * 0.50
        anchors.verticalCenter: parent.verticalCenter

        width: parent.width * .1
        height: parent.height

        color: ColorPalette.crimson
        radius: 10

        Text {
            anchors.centerIn: parent
            text: "-"
            color: ColorPalette.black
            font.pixelSize: 32
        }

        MouseArea {
            anchors.fill: parent
            onClicked: leftClicked()
        }
    }

    Item {
        id: middleArea
        x: parent.width * 0.60
        anchors.verticalCenter: parent.verticalCenter

        width: parent.width * .1
        height: parent.height

        Text {
            id: valueText
            anchors.centerIn: parent
            color: Theme.font1
            font.pixelSize: 22
        }
    }

    Rectangle {
        id: rightButton
        x: parent.width * 0.70
        anchors.verticalCenter: parent.verticalCenter

        width: parent.width * .1
        height: parent.height

        color: ColorPalette.softGreen
        radius: 10

        Text {
            anchors.centerIn: parent
            text: "+"
            color: ColorPalette.black
            font.pixelSize: 32
        }

        MouseArea {
            anchors.fill: parent
            onClicked: rightClicked()
        }
    }
}