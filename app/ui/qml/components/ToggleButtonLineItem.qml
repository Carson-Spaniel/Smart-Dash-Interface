import QtQuick

Item {
    property alias label: label.text
    property alias valueText: button.buttonText
    property alias buttonColor: button.color
    signal toggleButtonClicked()

    anchors.horizontalCenter: parent.horizontalCenter
    width: parent.width
    height: parent.height * .1
    y: parent.height * .1

    Text {
        id: label
        x: parent.width * 0.20
        anchors.verticalCenter: parent.verticalCenter
        text: label
        color: Theme.font1
        font.pixelSize: 40
    }

    ButtonItem {
        id: button
        buttonText: valueText
        color: buttonColor
        onButtonClicked: {
            toggleButtonClicked()
        }
        x: parent.width * .6
        anchors.verticalCenter: parent.verticalCenter
    }

}