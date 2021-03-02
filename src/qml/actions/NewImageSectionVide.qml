import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

BasePageAction {
    icon.source: "qrc:///icons/newImageSectionVide"
    nom: "ImageSectionVide"
    onTriggered: dialog.open()
    tooltip: "Créer un dessin vide"
    shortcut: ""

    dialog: Dialog {
        id: videdialog

        padding: 0
        y: parent.y + parent.height
        implicitWidth: 100
        title: ""
        focus: true

        background: Rectangle {
            anchors.fill: parent
            color: "lightgrey"
        }

        contentItem: RowLayout {
            property var sizes: {
                "petit": {
                    "iconHeight": 20,
                    "value": 400
                },
                "moyen": {
                    "iconHeight": 40,
                    "value": 800
                },
                "grand": {
                    "iconHeight": 60,
                    "value": 1200
                }
            }

            function choose(val) {
                //                    "position": newPos

                var newPos = append ? page.model.count : position + 1;
                page.addSection("ImageSection", newPos, {
                    "height": val,
                    "width": 1280
                });
                videdialog.close();
            }

            ImageVideButton {
                size: parent.sizes.petit
            }

            ImageVideButton {
                size: parent.sizes.moyen
            }

            ImageVideButton {
                size: parent.sizes.grand
            }

        }
        //          onAccepted: {

    }

}
