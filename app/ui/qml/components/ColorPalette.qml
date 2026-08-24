pragma Singleton

import QtQuick

QtObject {
    // ===============================================================
    // Basic Colors
    // ===============================================================

    readonly property color red: "#ff0000"
    readonly property color crimson: "#ff3030"
    readonly property color darkRed: "#8b0000"
    readonly property color firebrick: "#b22222"

    readonly property color orange: "#ffa500"
    readonly property color darkOrange: "#ff8c00"
    readonly property color coral: "#ff7f50"
    readonly property color tomato: "#ff6347"

    readonly property color yellow: "#ffff00"
    readonly property color gold: "#ffd700"
    readonly property color lightYellow: "#ffffe0"
    readonly property color lemonChiffon: "#fffacd"

    readonly property color green: "#00ff00"
    readonly property color darkGreen: "#006400"
    readonly property color forestGreen: "#228b22"
    readonly property color softGreen: "#00d26a"
    readonly property color lightGreen: "#90ee90"
    readonly property color paleGreen: "#98fb98"
    readonly property color springGreen: "#00ff7f"

    readonly property color cyan: "#00ffff"
    readonly property color aqua: "#00ffff"
    readonly property color turquoise: "#40e0d0"
    readonly property color teal: "#008080"

    readonly property color blue: "#0096ff"
    readonly property color darkBlue: "#00008b"
    readonly property color navy: "#000080"
    readonly property color mediumBlue: "#0000cd"
    readonly property color royalBlue: "#4169e1"
    readonly property color lightBlue: "#add8e6"
    readonly property color skyBlue: "#87ceeb"
    readonly property color deepSkyBlue: "#00bfff"

    readonly property color purple: "#b400ff"
    readonly property color magenta: "#ff00ff"
    readonly property color violet: "#ee82ee"
    readonly property color orchid: "#da70d6"
    readonly property color lavender: "#e6e6fa"

    readonly property color pink: "#ffc0cb"
    readonly property color hotPink: "#ff69b4"

    readonly property color darkPurple: "#4b0082"
    readonly property color indigo: "#4b0082"

    readonly property color maroon: "#800000"

    readonly property color brown: "#8b4513"
    readonly property color darkBrown: "#654321"
    readonly property color sienna: "#a0522d"
    readonly property color saddleBrown: "#8b4513"

    readonly property color black: "#000000"
    readonly property color white: "#ffffff"

    readonly property color gray: "#888888"
    readonly property color lightGray: "#d3d3d3"
    readonly property color slateGray: "#101010"
    readonly property color darkGray: "#303030"
    readonly property color silver: "#c0c0c0"

    readonly property color dark: "#3c3c3c"

    // ===============================================================
    // Palette List
    // ===============================================================
    //
    // This order intentionally matches your old Python COLORS list.
    //

    readonly property var colors: [
        red,
        darkRed,
        crimson,
        firebrick,

        orange,
        darkOrange,
        coral,
        tomato,

        yellow,
        gold,
        lightYellow,
        lemonChiffon,

        green,
        darkGreen,
        forestGreen,
        softGreen,
        lightGreen,
        paleGreen,
        springGreen,

        cyan,
        aqua,
        turquoise,
        teal,

        blue,
        darkBlue,
        navy,
        mediumBlue,
        royalBlue,
        lightBlue,
        skyBlue,
        deepSkyBlue,

        purple,
        magenta,
        violet,
        orchid,
        lavender,

        pink,
        hotPink,

        darkPurple,
        indigo,

        maroon,

        brown,
        darkBrown,
        sienna,
        saddleBrown,

        black,
        white,
        gray,
        lightGray,
        slateGray,
        darkGray,
        silver,

        dark
    ]

    // ===============================================================
    // Useful UI Colors
    // ===============================================================

    readonly property color background: "#080808"
    readonly property color panel: "#181818"
    readonly property color panelLight: "#202020"
    readonly property color border: "#303030"

    readonly property color text: "#f2f2f2"
    readonly property color textSecondary: "#888888"

    readonly property color success: green
    readonly property color warning: yellow
    readonly property color danger: red

    readonly property color inactive: "#303030"
}