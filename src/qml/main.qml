import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.14
import QtQuick.Window 2.14
import "divers"
import "matiere"
import "page"

ApplicationWindow {
    id: root

    width: 800
    height: 600
    visible: true
    title: "MyCartable: année " + ddb.anneeActive + "/" + (ddb.anneeActive + 1)
    onClosing: {
        baseItem.destroy(); // elmine presque tous les messages d'erreur
    }

    Rectangle {
        id: baseItem

        function showToast(message) {
            toast.msg = message;
            toast.open();
        }

        objectName: "baseItem"
        height: root.height - mainMenuBar.height
        width: root.width
        color: ddb.colorFond
        Component.onCompleted: {
            uiManager.sendToast.connect(showToast);
        }

        RowLayout {
            anchors.fill: parent
            spacing: 10

            // margin left
            Rectangle {
                Layout.fillHeight: true
            }

            RecentsRectangle {
                id: _recentsRectangle

                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: ddb.getLayoutSizes("preferredSideWidth")
                Layout.maximumWidth: ddb.getLayoutSizes("maximumSideWidth")
                Layout.minimumWidth: ddb.getLayoutSizes("minimumSideWidth")
            }

            PageRectangle {
                id: _pageRectangle

                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: ddb.getLayoutSizes("preferredCentralWidth")
                Layout.minimumWidth: ddb.getLayoutSizes("minimumCentralWidth")
            }

            MatiereRectangle {
                id: _matiereRectangle

                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: ddb.getLayoutSizes("preferredSideWidth")
                Layout.maximumWidth: ddb.getLayoutSizes("maximumSideWidth")
                Layout.minimumWidth: ddb.getLayoutSizes("minimumSideWidth")
            }
            // margin left

            Rectangle {
                Layout.fillHeight: true
            }

        }

        Toast {
            id: toast
        }

    }

    header: MainMenuBar {
        id: mainMenuBar
    }

}
