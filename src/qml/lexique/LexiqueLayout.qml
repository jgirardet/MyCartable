import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    property alias tableau: tableau_id
    property alias inserter: lexique_insert

    anchors.fill: parent

    Lexique {
        id: lexique_id

        parent: root
    }

    ColumnLayout {
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: tableau_id.width

        LexiqueInsert {
            id: lexique_insert

            lexique: lexique_id
            Layout.preferredHeight: 50
        }

        LexiqueTableau {
            id: tableau_id

            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: content.childrenRect.width
            Layout.fillHeight: true
            lexique: lexique_id
        }

    }

}
