import QtQuick

Item {
    id: root

    property int pageCount: 1
    property int currentPage: 0

    anchors.horizontalCenter: parent.horizontalCenter
    anchors.bottom: parent.bottom
    anchors.bottomMargin: 8

    width: (pageCount-1) * 30
    height: 30

    Row {
        anchors.fill: parent

        spacing: 8

        Repeater {
            model: root.pageCount

            delegate: Rectangle {
                width: 15
                height: 15

                radius: 7.5

                color: index === root.currentPage
                       ? "#ffffff"
                       : "#404040"
            }
        }
    }
}