import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Window 2.12

ApplicationWindow {
    id: root
    width: 800
    height: 600
    visible: true
    property  int headersHeight: 50
    property  real pageColumnWidthRatio: 2/3
    property  real lateralsColumnWidth: width * (1-pageColumnWidthRatio)/2
    property  real pageColumnWidth: width * pageColumnWidthRatio


    header : MainMenuBar {id: mainMenuBar }

    Item {
        id: baseItem
        Rectangle {
            id : recentsColumn
            color: "blue"
            height: root.height
            width: lateralsColumnWidth
            anchors.top: baseItem.top
            anchors.margins: 5

            ListView {
                id: rencentsListView
                model: [root.pageColumnWidthRatio,root.lateralsColumnWidth,'omkmoekom','omkmokozm','omkzmokom','omkmoekom','omkmoekom','omkmozkom','omkmokzom','omkmokzom','omkzmokom','omkmoekom','omkmoekom','omkmozkom','omkmokzom','omkmokzom']
                header : Rectangle {
                    id: recentsHeader
                    height: root.headersHeight
                    width: rencentsListView.width
                    z: 2
                    Label {
                            text:"Récents"
                            anchors.centerIn: parent
                            }
                      }
                headerPositioning: ListView.OverlayHeader


                anchors.top: recentsColumn.top
                height: parent.height
                width: parent.width
                clip: true
                delegate: Button {
                    text: modelData
                    width: rencentsListView.width
                    height: 40
                    }
            }
        }

        Rectangle {
            id: pageColumn
            anchors.top: baseItem.top
            anchors.left:  recentsColumn.right
            color: "red"
            height: root.height
            width: root.pageColumnWidth
            anchors.margins: 5

            Column {
                ToolBar {
                    width: pageColumn.width
                    height: root.headersHeight
                }
            }
        }

        Rectangle {
            id: matiereColumn
            anchors.top: baseItem.top
            anchors.margins: 5
            color: "yellow"
            anchors.left:  pageColumn.right
            height: root.height
            width: root.lateralsColumnWidth

            Rectangle {
                id: matiereSelect
                height: root.headersHeight
                width: root.lateralsColumnWidth
                Button {text: "MAtiere En Cours";anchors.fill: parent}
            }

            ListView {
                id: lessonsListView
                model: ['omkmokom','omkmokoem','omkmoekom','omkmokozm','omkzmokom','omkmoekom','omkmoekom','omkmozkom','omkmokzom','omkmokzom','omkzmokom','omkmoekom','omkmoekom','omkmozkom','omkmokzom','omkmokzom']
                property int commonHeight: 30
                header : Rectangle {
                    id: lessonsHeader
                    height: ListView.view.commonHeight
                    color : "purple"
                    width: lessonsListView.width
                    z: 2
                    Label {
                            text:"Leçons"
                            anchors.centerIn: parent
                            }
                      }
                headerPositioning: ListView.OverlayHeader


                anchors.top: matiereSelect.bottom
                height: (parent.height - matiereSelect.height)/2
                width: parent.width
                clip: true
                delegate: Button {
                    text: modelData
                    width: lessonsListView.width
                    height: ListView.view.commonHeight
                    }
            }

            ListView {
                id: exercicesListView
                model: ['omkmokom','omkmokoem','omkmoekom','omkmokozm','omkzmokom','omkmoekom','omkmoekom','omkmozkom','omkmokzom','omkmokzom','omkzmokom','omkmoekom','omkmoekom','omkmozkom','omkmokzom','omkmokzom']
                property int commonHeight: 30
                header : Rectangle {
                    id: exercicesHeader
                    height: ListView.view.commonHeight
                    color : "purple"
                    width: ListView.view.width
                    z: 2
                    Label {
                            text:"Leçons"
                            anchors.centerIn: parent
                            }
                      }
                headerPositioning: ListView.OverlayHeader


                anchors.top: lessonsListView.bottom
                height: (parent.height - matiereSelect.height)/2
                width: parent.width
                clip: true
                delegate: Button {
                    text: modelData
                    width: ListView.view.width
                    height: ListView.view.commonHeight
                    }
            }

        }

    }



 }