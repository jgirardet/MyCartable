import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.14

Rectangle {
    id: base

    color: ddb.colorFond

    ColumnLayout {
        id: activitesColumn

        anchors.fill: parent
        spacing: 5

        Rectangle {
            id: matiereSelect

            objectName: "matiereSelect"
            Layout.preferredHeight: ddb.getLayoutSizes("preferredHeaderHeight")
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
                model: ddb.matieresList
                currentIndex: ddb.getMatiereIndexFromId(ddb.currentMatiere)
                onActivated: {
                    ddb.setCurrentMatiereFromIndexSignal(index);
                }
                Component.onCompleted: {
                    activated.connect(ddb.setCurrentMatiereFromIndexSignal);
                }

                popup.background: Rectangle {
                    color: "transparent"
                }

                contentItem: Text {
                    text: combo.displayText
                    color: combo.currentValue ? combo.model[combo.currentIndex].fgColor : "white"
                    font.pointSize: 16
                    font.family: ddb.fontMain
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
                }

                background: Rectangle {
                    color: combo.currentValue ? combo.model[combo.currentIndex].bgColor : "white"
                    radius: 15
                }
                //        highlightedIndex:

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

            objectName: "repeater"
            model: ddb.pagesParSection
            Layout.fillHeight: true
            Layout.fillWidth: true
            spacing: 15
            clip: true

            delegate: ActiviteRectangle {
                model: modelData
                width: lvActivite.width
            }

        }

    }

}
