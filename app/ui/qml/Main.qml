import QtQuick
import QtQuick.Window
import QtQuick.Controls

Window {
    id: root

    // ===============================================================
    // Window
    // ===============================================================

    width: 960
    height: 544

    minimumWidth: 800
    minimumHeight: 480

    visible: true

    title: "Smart Dash"

    color: "#111111"

    // ===============================================================
    // FIXED DESIGN RESOLUTION
    // ===============================================================
    //
    // Every page is designed inside this coordinate system.
    //

    readonly property real designWidth: 1600
    readonly property real designHeight: 960

    readonly property real uiScale: Math.min(
        width / designWidth,
        height / designHeight
    )

    // ===============================================================
    // Page State
    // ===============================================================

    property int currentPage: dashboardPage

    readonly property int dashboardPage: 0
    readonly property int rpmPage: 1
    readonly property int settingsPage: 2
    readonly property int diagnosticsPage: 3
    readonly property int customizationPage: 4
    readonly property int shiftLightPage: 5
    readonly property int systemPage: 6

    readonly property int pageCount: 7

    // ===============================================================
    // VIEWPORT
    // ===============================================================
    //
    // This represents the actual Window.
    //

    Item {
        id: viewport

        anchors.fill: parent

        // ===========================================================
        // FIXED 1600x960 CANVAS
        // ===========================================================

        Item {
            id: canvas

            width: root.designWidth
            height: root.designHeight

            anchors.centerIn: parent

            transform: Scale {
                origin.x: canvas.width / 2
                origin.y: canvas.height / 2

                xScale: root.uiScale
                yScale: root.uiScale
            }

            // =======================================================
            // PAGE STACK
            // =======================================================

            StackView {
                id: pageStack

                anchors.fill: parent

                initialItem: dashboardComponent

                replaceEnter: Transition {
                    NumberAnimation {
                        property: "opacity"

                        from: 0.0
                        to: 1.0

                        duration: 150
                    }
                }

                replaceExit: Transition {
                    NumberAnimation {
                        property: "opacity"

                        from: 1.0
                        to: 0.0

                        duration: 150
                    }
                }
            }

            // =======================================================
            // DESIGN BORDER
            // =======================================================
            //
            // This shows the exact 1600x960 design boundary.
            //

            Rectangle {
                id: designBorder

                anchors.fill: parent

                color: "transparent"

                border.width: 4
                border.color: "red"

                z: 9999

                visible: true
            }
        }
    }

    // ===============================================================
    // Dashboard
    // ===============================================================

    Component {
        id: dashboardComponent

        Dashboard {
        }
    }

    // ===============================================================
    // RPM Settings
    // ===============================================================

    Component {
        id: rpmComponent

        RpmSettings {
            pageCount: root.pageCount
            pageIndex: root.rpmPage
        }
    }

    // ===============================================================
    // Settings
    // ===============================================================

    Component {
        id: settingsComponent

        Settings {
            pageCount: root.pageCount
            pageIndex: root.settingsPage
        }
    }

    // ===============================================================
    // Diagnostics
    // ===============================================================

    Component {
        id: diagnosticsComponent

        Diagnostics {
            pageCount: root.pageCount
            pageIndex: root.diagnosticsPage
        }
    }

    // ===============================================================
    // Customization
    // ===============================================================

    Component {
        id: customizationComponent

        Customization {
            pageCount: root.pageCount
            pageIndex: root.customizationPage
        }
    }

    // ===============================================================
    // Shift Light Settings
    // ===============================================================

    Component {
        id: shiftLightComponent

        ShiftLightSettings {
            pageCount: root.pageCount
            pageIndex: root.shiftLightPage
        }
    }

    // ===============================================================
    // System Information
    // ===============================================================

    Component {
        id: systemComponent

        SystemInformation {
            pageCount: root.pageCount
            pageIndex: root.systemPage
        }
    }

    // ===============================================================
    // Navigation
    // ===============================================================

    function navigateTo(page) {

        if (page < 0 || page >= pageCount)
            return

        if (page === currentPage)
            return

        currentPage = page

        switch (page) {

        case dashboardPage:
            pageStack.replace(dashboardComponent)
            break

        case rpmPage:
            pageStack.replace(rpmComponent)
            break

        case settingsPage:
            pageStack.replace(settingsComponent)
            break

        case diagnosticsPage:
            pageStack.replace(diagnosticsComponent)
            break

        case customizationPage:
            pageStack.replace(customizationComponent)
            break

        case shiftLightPage:
            pageStack.replace(shiftLightComponent)
            break

        case systemPage:
            pageStack.replace(systemComponent)
            break
        }
    }

    // ===============================================================
    // Next Page
    // ===============================================================

    function nextPage() {
        var next = (currentPage + 1) % pageCount

        navigateTo(next)
    }

    // ===============================================================
    // Previous Page
    // ===============================================================

    function previousPage() {
        var previous =
            (currentPage - 1 + pageCount)
            % pageCount

        navigateTo(previous)
    }

    // ===============================================================
    // Dashboard
    // ===============================================================

    function goToDashboard() {
        navigateTo(dashboardPage)
    }

    // ===============================================================
    // LEFT NAVIGATION
    // ===============================================================

    MouseArea {
        id: leftNavigation

        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom

        width: parent.width * 0.1

        z: 10000

        onClicked: {
            root.previousPage()
        }
    }

    // ===============================================================
    // RIGHT NAVIGATION
    // ===============================================================

    MouseArea {
        id: rightNavigation

        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom

        width: parent.width * 0.1

        z: 10000

        onClicked: {
            root.nextPage()
        }
    }
}