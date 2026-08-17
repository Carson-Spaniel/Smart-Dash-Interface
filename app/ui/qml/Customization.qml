import QtQuick
import "components"

Item {
    id: root

    property int pageCount: 1
    property int pageIndex: 1
    property var settings: settingsManager

    Rectangle {
        anchors.fill: parent

        color: Theme.background1
    }

    // ===============================================================
    // TITLE
    // ===============================================================

    Text {
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.05

        anchors.horizontalCenter: parent.horizontalCenter

        text: "Customization Settings"

        color: Theme.font1

        font.pixelSize: 28
        font.bold: true
    }

    // ===============================================================
    // FONT 1 COLOR
    // ===============================================================

    Text {
        x: parent.width * 0.20
        y: parent.height * 0.20

        text: "Font Color 1"

        color: Theme.font1

        font.pixelSize: 22
    }

    ColorSelector {
        x: parent.width * 0.50
        y: parent.height * 0.15

        width: parent.width * 0.30
        height: parent.height * 0.10

        colorIndex: Number(settings.font1ColorIndex)

        onChanged: function(index) {
            settings.font1ColorIndex = index
        }
    }

    // ===============================================================
    // FONT 2 COLOR
    // ===============================================================

    Text {
        x: parent.width * 0.20
        y: parent.height * 0.32

        text: "Font Color 2"

        color: Theme.font1

        font.pixelSize: 22
    }

    ColorSelector {
        x: parent.width * 0.50
        y: parent.height * 0.27

        width: parent.width * 0.30
        height: parent.height * 0.10

        colorIndex: Number(settings.font2ColorIndex)

        onChanged: function(index) {
            settings.font2ColorIndex = index
        }
    }

    // ===============================================================
    // BACKGROUND COLOR 1
    // ===============================================================

    Text {
        x: parent.width * 0.20
        y: parent.height * 0.44

        text: "Background Color 1"

        color: Theme.font1

        font.pixelSize: 22
    }

    ColorSelector {
        x: parent.width * 0.50
        y: parent.height * 0.39

        width: parent.width * 0.30
        height: parent.height * 0.10

        colorIndex: Number(settings.background1ColorIndex)

        onChanged: function(index) {
            settings.background1ColorIndex = index
        }
    }

    // ===============================================================
    // BACKGROUND COLOR 2
    // ===============================================================

    Text {
        x: parent.width * 0.20
        y: parent.height * 0.56

        text: "Background Color 2"

        color: Theme.font1

        font.pixelSize: 22
    }

    ColorSelector {
        x: parent.width * 0.50
        y: parent.height * 0.51

        width: parent.width * 0.30
        height: parent.height * 0.10

        colorIndex: Number(settings.background2ColorIndex)

        onChanged: function(index) {
            settings.background2ColorIndex = index
        }
    }

    // ===============================================================
    // BACKGROUND IMAGE
    // ===============================================================

    Text {
        x: parent.width * 0.20
        y: parent.height * 0.68

        text: "Background Image"

        color: Theme.font1

        font.pixelSize: 22
    }

    Rectangle {
        x: parent.width * 0.50
        y: parent.height * 0.63

        width: parent.width * 0.30
        height: parent.height * 0.10

        color: ColorPalette.panelLight

        border.width: 2
        border.color: ColorPalette.border

        radius: 4

        Text {
            anchors.centerIn: parent

            text: "IMAGE "
                  + (settings.backgroundImageIndex + 1)

            color: Theme.font1

            font.pixelSize: 14
        }
    }

    // ===============================================================
    // PAGE INDICATORS
    // ===============================================================

    PageIndicator {
        pageCount: root.pageCount
        currentPage: root.pageIndex
    }
}