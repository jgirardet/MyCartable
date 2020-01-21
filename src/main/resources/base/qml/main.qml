import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Window 2.12
import QtQuick.Layouts 1.12
//import RecentsModel 1.0



ApplicationWindow {
    id: root
    width: 800
    height: 600
    visible: true


    // Global models
//    RecentsModel{id: recentsModel}

    header: MainMenuBar {
        id: mainMenuBar
    }


    Item {
        id: baseItem
        objectName: "baseItem"
        height: root.height - mainMenuBar.height
        width: root.width

        RowLayout {
        anchors.fill:parent
        RecentsRectangle {
            id: _recentsRectangle
            ddb: database
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredWidth: database.getLayoutSizes("preferredSideWidth")
            Layout.maximumWidth: database.getLayoutSizes("maximumSideWidth")
            Layout.minimumWidth: database.getLayoutSizes("minimumSideWidth")


        }
        PageRectangle {
            id: _pageRectangle
            ddb: database
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredWidth: database.getLayoutSizes("preferredCentralWidth")
            Layout.minimumWidth: database.getLayoutSizes("minimumCentralWidth")


        }
        MatiereRectangle {
            id: _matiereRectangle
            ddb: database
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredWidth: database.getLayoutSizes("preferredSideWidth")
            Layout.maximumWidth: database.getLayoutSizes("maximumSideWidth")
            Layout.minimumWidth: database.getLayoutSizes("minimumSideWidth")

        }
    }
    }
}
