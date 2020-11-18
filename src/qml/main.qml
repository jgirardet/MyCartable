import Qt.labs.qmlmodels 1.0
import Qt.labs.qmlmodels 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import "qrc:/qml/divers"
import "qrc:/qml/layouts"
import "qrc:/qml/menu"

ApplicationWindow {
    id: root

    property alias mainItem: mainitem
    property alias toast: toast

    width: 800
    height: 600
    visible: true
    title: "MyCartable: année " + ddb.anneeActive + "/" + (ddb.anneeActive + 1)

    BusyIndicator {
        id: busy

        width: root.width / 4
        height: width
        anchors.centerIn: mainitem
        running: uiManager.buzyIndicator ?? false
        onRunningChanged: {
            if (running)
                mainitem.enabled = false;
            else
                mainitem.enabled = true;
        }
        z: running ? 10 : -5
    }

    Toast {
        id: toast

        function showToast(message) {
            // pas compris le bug
            //pas possible de bouger dans la déclaration
            if (root === null)
                return ;

            toast.msg = message;
            toast.open();
        }

        Component.onCompleted: {
            uiManager.sendToast.connect(toast.showToast);
        }
    }

    MainMenuBar {
        id: mainmenubar

        mainItem: mainitem
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
    }

    SplitLayout {
        id: mainitem

        anchors.top: mainmenubar.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        layouts: uiManager.mainLayouts
        nullComp: uiManager.nullComp
        initDataModel: ["classeur"]
    }

}
