import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.14

ColumnLayout {
    id: activitesColumn

    required property QtObject classeur
    property QtObject dispatcher: classeur.matieresDispatcher
    property QtObject matiere: classeur.currentMatiere
    property alias chooser: combo
    property alias activites: lvActivite

    anchors.fill: parent
    spacing: 5

    Database {
        id: database
    }

    Rectangle {
        id: matiereSelect

        objectName: "matiereSelect"
        Layout.preferredHeight: database.getConfig("preferredHeaderHeight")
        Layout.minimumHeight: Layout.preferredHeight
        Layout.maximumHeight: Layout.preferredHeight
        color: "transparent"
        Layout.fillWidth: true

        ComboBox {
            id: combo

            width: parent.width
            anchors.fill: parent
            textRole: "nom"
            valueRole: "id"
            objectName: "combo"
            model: dispatcher ? dispatcher.matieresList : []
            currentIndex: classeur.currentMatiereIndex
            onActivated: classeur.setCurrentMatiere(index)

            popup.background: Rectangle {
                color: "transparent"
            }

            contentItem: Text {
                text: combo.displayText
                color: matiere ? matiere.fgColor : "white"
                font.pointSize: 16
                font.capitalization: Font.Capitalize
                font.bold: true
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                onTextChanged: {
                    font.pointSize = 16;
                    while (contentWidth > (width)) {
                        font.pointSize--;
                        if (font.pointSize <= 4)
                            break;

                    }
                }
                onWidthChanged: {
                    font.pointSize = 16;
                    while (contentWidth > (width)) {
                        font.pointSize--;
                        if (font.pointSize <= 4)
                            break;

                    }
                }
            }

            background: Rectangle {
                color: matiere ? matiere.bgColor : "white"
                radius: 15
            }

            delegate: Button {
                highlighted: combo ? combo.highlightedIndex === index : false
                width: combo.width

                contentItem: Text {
                    id: delegateContent

                    text: modelData.nom
                    color: modelData.fgColor
                    font.bold: highlighted ? true : false
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                }

                background: Rectangle {
                    color: modelData.bgColor
                    radius: 10
                    border.width: highlighted ? 3 : 1
                    border.color: Qt.darker(modelData.bgColor, 3)
                }

            }

        }

    }

    ListView {
        id: lvActivite

        model: matiere ? matiere.activites : []
        Layout.fillHeight: true
        Layout.fillWidth: true
        spacing: 15
        clip: true

        delegate: ActiviteRectangle {
            activite: modelData
            width: lvActivite.width
        }

    }

}
