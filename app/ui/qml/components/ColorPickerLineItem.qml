import QtQuick

Item {
    property alias label: label.text
    property alias colorIndex: colorSelector.colorIndex

    signal colorChanged(int index)

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

    ColorSelector {
        id: colorSelector
        x: parent.width * 0.50

        width: parent.width * 0.30
        height: parent.height * .85
        anchors.verticalCenter: parent.verticalCenter

        onChanged: function(index) {
            colorChanged(index)
        }
    }
}