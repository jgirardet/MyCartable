import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Window 2.12

ApplicationWindow {
    id: root
    width: 800
    height: 600
    visible: true
    property int headersHeight: 50
    property real pageColumnWidthRatio: 2 / 3
    property real lateralsColumnWidth: width * (1 - pageColumnWidthRatio) / 2
    property real pageColumnWidth: width * pageColumnWidthRatio

    header: MainMenuBar {
        id: mainMenuBar
    }

    Item {
        id: baseItem
        height: root.height - mainMenuBar.height
        width: root.width
        Rectangle {
            id: recentsRectangle
            color: "orange"
            height: baseItem.height
            width: lateralsColumnWidth
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.margins: 5

            Column {
                id : recentsColumn
                height: parent.height
                width: parent.width
                spacing: 5

                Rectangle {
                    id: recentsHeader
                    height: root.headersHeight
                    width: root.lateralsColumnWidth
                    RoundButton {
                        text: "Récents"
                        anchors.fill: parent
                        radius: 10
                        onClicked: console.log(root.height, baseItem.height, recentsRectangle.height, recentsColumn.height, recentsListView.height)
                    }
                 }

                RecentsListView {
                    id: recentsListView
//                    model: ddb.recents
                    model: ddb.withslot()
                }
            }
        }

        Rectangle {
            id: pageColumn
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.left: recentsRectangle.right
            anchors.margins: 5
            color: "red"
            height: baseItem.height
            width: root.pageColumnWidth

            Column {
                anchors.fill: parent
                spacing: 5
                ToolBar {
                    id: pageToolBar
                    width: pageColumn.width
                    height: root.headersHeight
                }
                Rectangle {
                    width: parent.width
                    height: parent.height -pageToolBar.height -parent.spacing
                    color: "green"
                }
            }
        }

        Rectangle {
            id: matiereRectangle
            anchors.top: baseItem.top
            anchors.margins: 5
            color: "yellow"
            anchors.left: pageColumn.right
            height: baseItem.height
            width: root.lateralsColumnWidth

            Column {
                id : activitesColumn
                height: matiereRectangle.height
                width: matiereRectangle.width
                spacing: 5
                property real activiteListViewsHeight: (matiereRectangle.height-matiereSelect.height-spacing*2)/2

                Rectangle {
                    id: matiereSelect
                    height: root.headersHeight
                    width: root.lateralsColumnWidth
                    Button {
                        text: "Français"
                        anchors.fill: parent
                        onClicked: console.log(matiereRectangle.height, activitesColumn.height, matiereSelect.height,lessonsListView.height)
                         }
                    }

                ActiviteListView {
                    id: lessonsListView
                    model: ['omkmokom', 'omkmokoem', 'omkmoekom', 'omkmokozm', 'omkzmokom', 'omkmoekom', 'omkmoekom', 'omkmozkom', 'omkmokzom', 'omkmokzom', 'omkzmokom', 'omkmoekom', 'omkmoekom', 'omkmozkom', 'omkmokzom', 'omkmokzom']
                    commonHeight: 30
                    headerText: "Leçons"
                    headerColor: "pink"
                    height: activitesColumn.activiteListViewsHeight
                }
                ActiviteListView {
                    model: ['omkmokom', 'omkmokoem', 'omkmoekom', 'omkmokozm', 'omkzmokom', 'omkmoekom', 'omkmoekom', 'omkmozkom', 'omkmokzom', 'omkmokzom', 'omkzmokom', 'omkmoekom', 'omkmoekom', 'omkmozkom', 'omkmokzom', 'omkmokzom']
                    commonHeight: 30
                    headerText: "Exercices"
                    headerColor: "orange"
                    height: activitesColumn.activiteListViewsHeight
                }
             }
        }
    }
}
