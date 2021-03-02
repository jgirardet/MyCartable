import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ColumnLayout {
    id: root

    required property QtObject quizz
    property int flagSize: 20
    property int pointSize: 12
    property alias input: textinput
    property alias reponse: reponse_id
    property alias question: question_id
    property alias anteriorite: anteriorite_id

    anchors.fill: parent

    RowLayout {
        Layout.fillWidth: true
        Layout.alignment: Qt.AlignHCenter
        spacing: 20

        Button {
            text: "Recommencer"
            onClicked: {
                quizz.start();
                textinput.text = "";
                textinput.forceActiveFocus();
            }
            font.pointSize: root.pointSize
        }

        Label {
            text: "anteriorite (jours)"
            font.pointSize: root.pointSize
        }

        TextField {
            id: anteriorite_id

            Layout.preferredWidth: 50
            font.pointSize: root.pointSize
            Component.onCompleted: text = quizz.anteriorite
            onTextChanged: quizz.anteriorite = text ? parseInt(text) : 0
        }

        Item {
        }

    }

    RowLayout {
        Layout.alignment: Qt.AlignHCenter

        Label {
            text: "score"
            font.pointSize: root.pointSize
        }

        Label {
            text: quizz.score + "/" + quizz.total
            font.pointSize: root.pointSize
        }

    }

    RowLayout {
        Layout.fillWidth: true
        Layout.alignment: Qt.AlignHCenter

        Label {
            text: quizz.questionFlag
            font.pointSize: root.flagSize
        }

        Label {
            id: question_id

            text: quizz.question
            font.pointSize: root.pointSize
            Layout.margins: root.flagSize
        }

        Label {
            text: quizz.questionFlag
            font.pointSize: root.flagSize
        }

    }

    Label {
        id: reponse_id

        property string reponse: quizz.reponse

        Layout.fillWidth: true
        Layout.alignment: Qt.AlignHCenter
        horizontalAlignment: Qt.AlignHCenter
        text: quizz.showError ? `réponse: ${reponse}` : ""
        color: "red"
        font.pointSize: root.pointSize
    }

    RowLayout {
        Layout.fillWidth: true
        Layout.alignment: Qt.AlignHCenter

        Label {
            text: quizz.reponseFlag
            font.pointSize: root.flagSize
        }

        TextField {
            id: textinput

            onTextChanged: quizz.proposition = text
            onAccepted: {
                if (quizz.checkReponse())
                    text = "";

            }
            font.pointSize: root.pointSize
            Layout.margins: 20
            Layout.minimumWidth: 200
            Layout.minimumHeight: contentHeight + 20
            padding: 5

            background: Rectangle {
                border.width: 3
                border.color: "black"
            }

        }

        Label {
            text: quizz.reponseFlag
            font.pointSize: root.flagSize
        }

    }

}
