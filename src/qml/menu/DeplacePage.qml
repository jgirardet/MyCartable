import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15

Dialog {
    id: root

    property var model
    property int cellHeight: 20
    property string pageId
    property alias matieres: columnmatiere
    property QtObject rootClasseur: findClasseur(root)
    property alias buttons: ac_buttons

    function findClasseur(item) {
        if (item === null)
            return null;

        if (item.objectName !== "ClasseurLayout")
            return findClasseur(item.parent);
        else
            return item.classeur;
    }

    function ouvre(pageId, basebutton) {
        root.model = rootClasseur.matieresDispatcher.getDeplacePageModel();
        root.pageId = pageId;
        open();
    }

    contentHeight: 300
    contentWidth: 200
    margins: 0
    padding: 0

    Database {
        id: database
    }

    ScrollView {
        id: scroll

        anchors.fill: parent
        clip: true
        ScrollBar.vertical.policy: ScrollBar.AlwaysOff

        MouseArea {
            anchors.fill: parent
            onClicked: root.close()
        }

        Column {
            id: columnmatiere

            x: 100
            height: childrenRect.height
            width: 100

            Repeater {
                id: ac_buttons

                model: root.model

                delegate: Button {
                    id: matierebutton

                    property var activites: columnactivite
                    property var repActivites: rep_activites

                    highlighted: hovered
                    text: modelData.nom
                    height: root.cellHeight
                    width: parent.width
                    font.pointSize: 8

                    Column {
                        id: columnactivite

                        anchors.right: matierebutton.left
                        visible: matierebutton.hovered
                        width: 100
                        height: childrenRect.height
                        onVisibleChanged: {
                            var pointAsRoot = mapToItem(scroll, x, y);
                            var mapx = pointAsRoot.x;
                            var mapy = pointAsRoot.y;
                            if (mapy + height >= scroll.height)
                                y = mapFromItem(scroll, mapx, scroll.height - height - 1).y;

                        }

                        Repeater {
                            id: rep_activites

                            model: modelData.activites

                            delegate: Button {
                                id: activitebutton

                                property var reroot: root

                                height: root.cellHeight
                                width: 100
                                text: modelData.nom
                                highlighted: hovered
                                onClicked: {
                                    rootClasseur.movePage(root.pageId, modelData.id);
                                    reroot.close();
                                }

                                background: Rectangle {
                                    color: matierebutton.background.color
                                    anchors.fill: parent
                                }

                            }

                        }

                    }

                    background: Rectangle {
                        color: modelData.bgColor ?? "transparent"
                        anchors.fill: parent
                    }

                }

            }

        }

    }

    header: Label {
        id: titre

        width: 100
        height: 40
        text: "Déplacer vers"
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter

        background: Rectangle {
            anchors.fill: parent
            color: "lightgrey"
            border.color: "black"
            border.width: 2
        }

    }

    background: Rectangle {
        color: "transparent"
        border.width: 0
    }

}
