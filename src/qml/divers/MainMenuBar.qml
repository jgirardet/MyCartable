import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/configuration"

Control {
    id: root

    property alias changerAnnee: changerAnnee_id
    property alias heightAnimation: height_animation
    property alias hideTimer: timer_hide
    property Item mainItem
    property var base

    height: 2 // juste pour trigger le hover
    onHoveredChanged: {
        if (hovered) {
            root.state = "expanded";
            timer_hide.restart();
        }
    }
    hoverEnabled: true
    states: [
        State {
            name: "expanded"

            PropertyChanges {
                target: root
                height: root.contentItem.childrenRect.height
            }

        }
    ]

    Database {
        id: database
    }

    Annee {
        id: annee
    }

    Timer {
        id: timer_hide

        running: false
        repeat: false
        interval: 2000
        onTriggered: () => {
            if (root.hovered || menu.visible)
                timer_hide.restart();
            else
                return root.state = "";
        }
    }

    Dialog {
        id: changerAnnee_id

        objectName: "changerAnnee"
        height: 300
        width: 600
        title: "Cliquer sur l'année choisie"
        anchors.centerIn: Overlay.overlay
        standardButtons: Dialog.Cancel
        onOpened: {
            //to refresh
            contentItem.model = annee.getMenuAnnees();
        }

        contentItem: ListView {
            id: lv

            width: delegate.width
            height: 400 //delegate.height * count
            spacing: 5

            delegate: ValueButton {
                onClicked: {
                    database.setConfig('annee', value);
                    base.reload();
                    changerAnnee_id.close();
                }
                text: "mon année de " + modelData.niveau + " en " + modelData.id + "/" + (modelData.id + 1)
                value: modelData.id
            }

            footer: Button {
                text: "Ajouter une année"
                onClicked: newAnneeDialog.open()
            }

        }

    }

    NewAnnee {
        id: newAnneeDialog
    }

    Dialog {
        id: changer_matieres

        objectName: "changer_matieres"
        anchors.centerIn: Overlay.overlay
        height: root.parent.height * 0.9
        contentWidth: contentItem.width
        onClosed: {
            base.reload();
        }

        contentItem: ChangeGroupe {
            annee: database.getConfig("annee")
        }

    }

    contentItem: Row {
        height: childrenRect.height
        visible: root.state == "expanded"

        MenuBar {
            Menu {
                id: menu

                title: qsTr("&Fichier")

                Action {
                    text: qsTr("&Changer d'année")
                    onTriggered: changerAnnee.open()
                }

                Action {
                    text: qsTr("&Modifier les matières")
                    onTriggered: {
                        changer_matieres.open();
                    }
                }

            }

        }

        Repeater {
            id: flipbuttons

            model: [{
                "icon": "split_horizontal",
                "orientation": Qt.Horizontal,
                "contraire": Qt.Vertical
            }, {
                "icon": "split_vertical",
                "orientation": Qt.Vertical,
                "contraire": Qt.Horizontal
            }]

            delegate: Button {
                id: button_horizontal

                icon.source: "qrc:/icons/" + modelData.icon
                highlighted: mainItem.orientation == modelData.orientation && mainItem.count > 1
                onClicked: {
                    if (mainItem.orientation == modelData.contraire) {
                        mainItem.orientation = modelData.orientation;
                        if (mainItem.count > 1)
                            return ;

                    }
                    if (mainItem.count == 1)
                        mainItem.append("vide");
                    else
                        mainItem.pop();
                }
            }

        }

    }

    Behavior on height {
        NumberAnimation {
            id: height_animation

            duration: 300
        }

    }

}
