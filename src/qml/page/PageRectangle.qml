import MyCartable 1.0
import QtQml 2.15
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "qrc:/qml/menu"

Rectangle {
    id: root

    property QtObject page
    property alias titre: titre
    property alias loaderps: loaderps
    property alias busy: popup

    onPageChanged: {
        loaderps.reload();
        if (page && page.titre == "")
            titre.forceActiveFocus();

    }
    color: Qt.rgba(98 / 255, 105 / 255, 123 / 255, 1)

    Database {
        id: database
    }

    PageToolBar {
        id: pageToolBar

        page: root.page
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 10
        height: database.getConfig("preferredHeaderHeight")
    }

    PageTitre {
        id: titre

        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: pageToolBar.bottom
        height: 50
        page: root.page
        anchors.margins: 10
        visible: page
    }

    Loader {
        id: loaderps

        property bool populated: item ? item.populated : false

        function reload() {
            state = "";
            source = "";
            if (page)
                setSource("qrc:/qml/page/PageSections.qml", {
                "page": root.page
            });

        }

        onPopulatedChanged: {
            if (populated)
                state = "visible";

        }
        asynchronous: true
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: titre.bottom
        anchors.bottom: parent.bottom
        anchors.margins: 10
        enabled: status == Loader.Ready
        opacity: 0
        states: [
            State {
                name: "visible"

                PropertyChanges {
                    target: loaderps
                    opacity: 1
                }

            }
        ]
        transitions: [
            Transition {
                to: "visible"

                PropertyAnimation {
                    target: loaderps
                    property: "opacity"
                    easing.type: Easing.Linear
                    duration: 1000
                }

            }
        ]
    }

    Popup {
        id: popup

        anchors.centerIn: Overlay.overlay
        parent: Overlay.overlay
        visible: loaderps.item && !loaderps.populated

        BusyIndicator {
            running: true
        }

        background: Rectangle {
            color: "transparent"
            anchors.fill: parent
        }

    }

}
