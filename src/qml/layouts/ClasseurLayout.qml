import MyCartable 1.0
import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "qrc:/qml/divers"
import "qrc:/qml/matiere"
import "qrc:/qml/page"

SandwichLayout {
    id: root

    property QtObject classeur
    property alias currentMatiere: classeurid.currentMatiere
    property int currentAnnee: globus.annee

    objectName: "ClasseurLayout"
    anchors.fill: parent
    color: ddb.colorFond

    Globus {
        id: globus

        Component.onCompleted: print(globus.annee)
    }

    classeur: Classeur {
        id: classeurid

        annee: root.currentAnnee
    }

    hamAndCheese: PageRectangle {
        id: _pageRectangle

        page: classeurid.page
    }

    rightBread: MatiereRectangle {
        id: matiere
    }

    leftBread: RecentsRectangle {
        id: recents
    }

}
