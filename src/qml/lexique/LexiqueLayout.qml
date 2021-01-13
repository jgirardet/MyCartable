import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root

    property alias tableau: tableau_id

    anchors.fill: parent

    Lexique {
        id: lexique_id

        parent: root
    }

    LexiqueTableau {
        id: tableau_id

        anchors.fill: parent
        lexique: lexique_id
    }

}
