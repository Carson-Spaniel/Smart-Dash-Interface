import QtQuick

Rectangle {
    property alias buttonText: buttonText.text
    signal buttonClicked()

    width: parent.width * .1
    height: parent.height * .85

    radius: 10

    Text {
        id: buttonText
        anchors.centerIn: parent
        color: ColorPalette.black
        font.pixelSize: 32
    }

    MouseArea {
        anchors.fill: parent
        onClicked: buttonClicked()
    }
}