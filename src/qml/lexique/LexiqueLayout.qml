import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    property alias tableau: tableau_id
    property alias inserter: lexique_insert
    property alias header: table_header

    anchors.fill: parent

    Lexique {
        id: lexique_id

        parent: root
    }

    Database {
        id: database_id
    }

    ColumnLayout {
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: tableau_id.width

        LexiqueInsert {
            id: lexique_insert

            lexique: lexique_id
            database: database_id
            Layout.preferredHeight: 50
        }

        LexiqueTableauHeader {
            id: table_header

            lexique: lexique_id
            database: database_id
            Layout.preferredWidth: tableau_id.width
            Layout.preferredHeight: 50
        }

        LexiqueContent {
            id: tableau_id

            lexique: lexique_id
            database: database_id
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: childrenRect.width
            Layout.fillHeight: true
        }

    }

}
