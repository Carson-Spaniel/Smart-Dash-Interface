import QtQuick

Item {
    property alias title: title.text
    anchors.top: parent.top
    width: parent.width
    height: parent.height * .1
    Text {
        id: title
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter

        color: Theme.font1

        font.pixelSize: 50
        font.bold: true
    }
}