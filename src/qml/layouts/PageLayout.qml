import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "qrc:/qml/divers"
import "qrc:/qml/matiere"
import "qrc:/qml/page"

SandwichLayout {
    id: root

    property Item view

    anchors.fill: parent
    color: ddb.colorFond

    hamAndCheese: PageRectangle {
        id: _pageRectangle
    }

    rightBread: MatiereRectangle {
        id: matiere
    }

    leftBread: RecentsRectangle {
        id: recents
    }

}
