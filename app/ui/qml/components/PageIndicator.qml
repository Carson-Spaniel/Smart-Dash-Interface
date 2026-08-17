import QtQuick

Item {
    id: root

    property int pageCount: 1
    property int currentPage: 0

    anchors.horizontalCenter: parent.horizontalCenter
    anchors.bottom: parent.bottom
    anchors.bottomMargin: 8

    width: (pageCount-1) * 16
    height: 16

    Row {
        anchors.fill: parent

        spacing: 8

        Repeater {
            model: root.pageCount

            delegate: Rectangle {
                width: 8
                height: 8

                radius: 4

                color: index === root.currentPage
                       ? "#ffffff"
                       : "#404040"
            }
        }
    }
}