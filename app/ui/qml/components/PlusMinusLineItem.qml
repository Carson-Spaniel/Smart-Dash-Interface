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
        font.pixelSize: 40
    }

    ButtonItem {
        buttonText: "-"
        color: ColorPalette.crimson
        onButtonClicked: leftClicked()
        x: parent.width * .5
        anchors.verticalCenter: parent.verticalCenter
    }

    Item {
        id: middleArea
        x: parent.width * 0.60
        anchors.verticalCenter: parent.verticalCenter

        width: parent.width * .1
        height: parent.height * .85

        Text {
            id: valueText
            anchors.centerIn: parent
            color: Theme.font1
            font.pixelSize: 32
        }
    }

    ButtonItem {
        buttonText: "+"
        color: ColorPalette.softGreen
        onButtonClicked: rightClicked()
        x: parent.width * .7
        anchors.verticalCenter: parent.verticalCenter
    }
}