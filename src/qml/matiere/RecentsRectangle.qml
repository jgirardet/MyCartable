import "../divers"
import "../menu"
import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.14

Rectangle {
    id: base

    color: ddb.colorFond

    ColumnLayout {
        MainMenuBar {
            id: mainmenubar

            Layout.fillWidth: true
            Layout.preferredHeight: 50
        }

        ListView {
            id: root

            Layout.preferredWidth: base.width
            Layout.preferredHeight: base.height
            model: ddb.recentsModel
            spacing: 5
            clip: true

            delegate: PageButton {
                height: contentItem.contentHeight + 20
                width: root.width
                model: modelData
            }

        }

    }

}
