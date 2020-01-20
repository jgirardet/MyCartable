import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Window 2.12
import QtQuick.Layouts 1.12
import RecentsModel 1.0



ApplicationWindow {
    id: root
    width: 800
    height: 600
    visible: true
    property int headersHeight: 50
    property real pageColumnWidthRatio: 2 / 3
    property real lateralsColumnWidth: width * (1 - pageColumnWidthRatio) / 2
    property real pageColumnWidth: width * pageColumnWidthRatio

    // Global models
    RecentsModel{id: recentsModel}

    header: MainMenuBar {
        id: mainMenuBar
    }

    Item {
        id: _itemDispatcher
        objectName: "_itemDispatcher"

        signal newPage(int activite)

         onNewPage: {
            var np = database.newPage(1)
            // Todo set PageListView
            recentsModel.modelReset()
            // Todo set partie matiere de droite
         }

    }

    Item {
        id: baseItem
        objectName: "baseItem"
        height: root.height - mainMenuBar.height
        width: root.width

        GridLayout {
        columns: 5
        RecentsRectangle {
            id: recentsRectangle
            ddb: database
            Layout.rowSpan: 1

        }

        PageRectangle {
            id: _pageRectangle
            ddb: database
            Layout.rowSpan: 3

        }

        MatiereRectangle {
            Layout.rowSpan: 1

        }
        }
    }

}
