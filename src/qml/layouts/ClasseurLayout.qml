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
    property int currentAnnee: database.getConfig("annee")

    objectName: "ClasseurLayout"
    anchors.fill: parent
    color: database.getConfig("colorFond")

    Database {
        id: database
    }

    classeur: Classeur {
        id: classeurid

        annee: root.currentAnnee
        onPageChanged: loader.reload(page)
    }

    hamAndCheese: Loader {
        id: loader

        function reload(page) {
            source = "";
            if (page)
                setSource("qrc:/qml/page/PageRectangle.qml", {
                "page": page
            });

        }

    }

    leftBread: RecentsRectangle {
        id: recentsid

        model: classeurid.recents
    }

    rightBread: MatiereRectangle {
        id: matiere

        classeur: classeurid
    }

}
