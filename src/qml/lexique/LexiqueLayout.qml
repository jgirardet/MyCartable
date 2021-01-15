import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root

    property alias tableau: tableau_id
    property alias inserter: lexique_insert
    property alias header: table_header
    property alias options: lexique_options
    property int columnWidth: database.getConfig("lexiqueColumnWidth")
    property int preferredHeight: 50

    color: "white"
    anchors.fill: parent

    Lexique {
        id: lexique_id

        parent: root
    }

    Database {
        id: database_id
    }

    ColumnLayout {
        anchors.leftMargin: 20
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: tableau_id.width

        LexiqueOptions {
            id: lexique_options

            lexique: lexique_id
            Layout.preferredHeight: root.preferredHeight
        }

        LexiqueInsert {
            id: lexique_insert

            lexique: lexique_id
            columnWidth: root.columnWidth
            Layout.preferredHeight: root.preferredHeight
        }

        LexiqueTableauHeader {
            id: table_header

            lexique: lexique_id
            columnWidth: root.columnWidth
            Layout.preferredWidth: childrenRect.width
            Layout.preferredHeight: root.preferredHeight
        }

        LexiqueContent {
            id: tableau_id

            lexique: lexique_id
            columnWidth: root.columnWidth
            rowHeight: root.preferredHeight
            Layout.preferredWidth: childrenRect.width
            Layout.fillHeight: true
        }

    }

}
