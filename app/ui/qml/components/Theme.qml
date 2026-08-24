pragma Singleton

import QtQuick

QtObject {
    // ===============================================================
    // Selected Application Colors
    // ===============================================================

    readonly property color font1:
        ColorPalette.colors[
            settingsManager.font1ColorIndex
        ]

    readonly property color font2:
        ColorPalette.colors[
            settingsManager.font2ColorIndex
        ]

    readonly property color background1:
        ColorPalette.colors[
            settingsManager.background1ColorIndex
        ]

    readonly property color background2:
        ColorPalette.colors[
            settingsManager.background2ColorIndex
        ]

    // ===============================================================
    // Standard UI Colors
    // ===============================================================

    readonly property color panel:
        ColorPalette.panel

    readonly property color panelLight:
        ColorPalette.panelLight

    readonly property color border:
        ColorPalette.border

    readonly property color textSecondary:
        ColorPalette.textSecondary

    readonly property color success:
        ColorPalette.success

    readonly property color warning:
        ColorPalette.warning

    readonly property color danger:
        ColorPalette.danger

    readonly property color inactive:
        ColorPalette.inactive

    readonly property color black:
        ColorPalette.black

    readonly property color white:
        ColorPalette.white

    readonly property color lightGray:
        ColorPalette.lightGray
}