import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/layouts"

Row {
    id: root

    property alias langues: repeater
    property alias quizz: quizz_id
    required property Item lexique

    spacing: 10

    Button {
        text: "Choisir les langues"
        onClicked: langues.open()
    }

    Button {
        id: quizz_button

        text: "quizz"
        onClicked: quizz_dialog.open()
    }

    SplitSwitch {
    }

    Dialog {
        id: quizz_dialog

        anchors.centerIn: Overlay.overlay
        width: 400
        height: 400
        onOpened: {
            if (lexique.quizz.question == "")
                lexique.quizz.start();

            quizz_id.input.forceActiveFocus();
        }

        Quizz {
            id: quizz_id

            quizz: lexique.quizz
        }

    }

    Dialog {
        id: langues

        height: grid.height
        width: grid.width

        Grid {
            id: grid

            columns: 3
            height: childrenRect.height + 50
            width: childrenRect.width + 100

            Repeater {
                id: repeater

                model: lexique.model.availablesLocales

                delegate: CheckBox {
                    checked: modelData.active
                    text: modelData.nom
                    onCheckedChanged: lexique.updateActivesLocales(modelData.id, checked)
                }

            }

        }

    }

}
