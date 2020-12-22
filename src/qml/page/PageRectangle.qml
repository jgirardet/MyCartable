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
    Component.onCompleted: {
        var newComp = Qt.createComponent("qrc:/qml/menu/MenuFlottantAnnotationDessin.qml");
        if (newComp.status == Component.Ready)
            uiManager.menuFlottantAnnotationDessin = newComp.createObject(root);
        else
            print(newComp.errorString());
        var newComp = Qt.createComponent("qrc:/qml/menu/MenuFlottantText.qml");
        if (newComp.status == Component.Ready)
            uiManager.menuFlottantText = newComp.createObject(root);
        else
            print(newComp.errorString());
        var newComp = Qt.createComponent("qrc:/qml/menu/MenuFlottantAnnotationText.qml");
        if (newComp.status == Component.Ready)
            uiManager.menuFlottantAnnotationText = newComp.createObject(root);
        else
            print(newComp.errorString());
        var newComp = Qt.createComponent("qrc:/qml/menu/MenuFlottantTableau.qml");
        if (newComp.status == Component.Ready)
            uiManager.menuFlottantTableau = newComp.createObject(root);
        else
            print(newComp.errorString());
        var newComp = Qt.createComponent("qrc:/qml/menu/MenuFlottantImage.qml");
        if (newComp.status == Component.Ready)
            uiManager.menuFlottantImage = newComp.createObject(root);
        else
            print(newComp.errorString());
    }
    Component.onDestruction: {
        uiManager.menuFlottantAnnotationDessin = null;
        uiManager.menuFlottantText = null;
        uiManager.menuFlottantAnnotationText = null;
        uiManager.menuFlottantTableau = null;
        uiManager.menuFlottantImage = null;
    }

    PageToolBar {
        id: pageToolBar

        page: root.page
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        height: ddb.getLayoutSizes("preferredHeaderHeight")
    }

    PageTitre {
        id: titre

        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: pageToolBar.bottom
        height: 50
        page: root.page
        anchors.margins: 20
        visible: page
    }

    Loader {
        //            titre.forceActiveFocus();

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
        anchors.topMargin: 20
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
