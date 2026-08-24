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

    TitleItem {
        title: "Customization Settings"
    }

    // ===============================================================
    // FONT 1 COLOR
    // ===============================================================

    ColorPickerLineItem {
        label: "Font Color 1"
        y: parent.height * .1
        colorIndex: Number(settings.font1ColorIndex)
        onColorChanged: function(index) {
            settings.font1ColorIndex = index
        }
    }

    // ===============================================================
    // FONT 2 COLOR
    // ===============================================================

    ColorPickerLineItem {
        label: "Font Color 2"
        y: parent.height * .2
        colorIndex: Number(settings.font2ColorIndex)
        onColorChanged: function(index) {
            settings.font2ColorIndex = index
        }
    }

    // ===============================================================
    // BACKGROUND COLOR 1
    // ===============================================================

    ColorPickerLineItem {
        label: "Background Color 1"
        y: parent.height * .3
        colorIndex: Number(settings.background1ColorIndex)
        onColorChanged: function(index) {
            settings.background1ColorIndex = index
        }
    }

    // ===============================================================
    // BACKGROUND COLOR 2
    // ===============================================================

    ColorPickerLineItem {
        label: "Background Color 2"
        y: parent.height * .4
        colorIndex: Number(settings.background2ColorIndex)
        onColorChanged: function(index) {
            settings.background2ColorIndex = index
        }
    }

    // ===============================================================
    // BACKGROUND IMAGE
    // ===============================================================

    // Text {
    //     x: parent.width * 0.20
    //     y: parent.height * 0.68

    //     text: "Background Image"

    //     color: Theme.font1

    //     font.pixelSize: 22
    // }

    // Rectangle {
    //     x: parent.width * 0.50
    //     y: parent.height * 0.63

    //     width: parent.width * 0.30
    //     height: parent.height * 0.10

    //     color: ColorPalette.panelLight

    //     border.width: 2
    //     border.color: ColorPalette.border

    //     radius: 4

    //     Text {
    //         anchors.centerIn: parent

    //         text: "IMAGE "
    //               + (settings.backgroundImageIndex + 1)

    //         color: Theme.font1

    //         font.pixelSize: 14
    //     }
    // }

    // ===============================================================
    // PAGE INDICATORS
    // ===============================================================

    PageIndicator {
        pageCount: root.pageCount
        currentPage: root.pageIndex
    }
}