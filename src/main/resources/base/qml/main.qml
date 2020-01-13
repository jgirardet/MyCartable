import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Window 2.12
import RecentsModel 1.0




ApplicationWindow {
    id: root
    width: 800
    height: 600
    visible: true
    property int headersHeight: 50
    property real pageColumnWidthRatio: 2 / 3
    property real lateralsColumnWidth: width * (1 - pageColumnWidthRatio) / 2
    property real pageColumnWidth: width * pageColumnWidthRatio

    // Global models
    RecentsModel{id: recentsModel}

    header: MainMenuBar {
        id: mainMenuBar
    }

    Item {
        id: _itemDispatcher

        signal newPage(int activite)
        signal changePage(int id)
        signal changeMatiere(string matiereNom)

         onNewPage: {
            var np = ddb.newPage(1)
            ddb.currentMatiere = 3
            // Todo set PageListView
            recentsModel.modelReset()
            // Todo set partie matiere de droite
         }

         onChangePage: {
            var page = ddb.getPageById(id)
            print(page.id, page.titre, page.matiere)
            changeMatiere(page.matiereNom)
            _comboBoxSelectMatiere.currentIndex = _comboBoxSelectMatiere.find(page.matiereNom)
            print(page.activite)
         }

         onChangeMatiere: {
            print(matiereNom)
         }
//         Connections {
//            target: ddb
//            onSNewPage: {
//            print(lid['az'])
//            print(ddb.withslot())
//            }
//         }


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

                RoundButton {
                    id: recentsHeader
                    height: root.headersHeight
                    width: root.lateralsColumnWidth
                    text: "Récents" + ddb.currentMatiere
                    radius: 10
                 }

                RecentsListView {
                    id: recentsListView
                    model: recentsModel
                    onItemClicked: _itemDispatcher.changePage(id)

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

                PageToolBar {
                    id: pageToolBar
                    width: pageColumn.width
                    height: root.headersHeight
                    onNouveau: _itemDispatcher.newPage(2)
                   }
                Rectangle {
                    width: parent.width
                    height: parent.height -pageToolBar.height -parent.spacing
                    color: "green"
                    PageListView{model:[1,2,3,4,5,]}
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
                    MatiereComboBox {
                        id: _comboBoxSelectMatiere
                        model: ddb.matiereNoms()
                        onCurrentTextChanged: _itemDispatcher.changeMatiere(currentText)
                    }
                }

                ActiviteListView {
                    id: _listViewLessons
                    model: ddb.getPagesByMatiereAndActivite(_comboBoxSelectMatiere.currentText, 0)
                    commonHeight: 30
                    headerText: "Leçons"
                    headerColor: "pink"
                    height: activitesColumn.activiteListViewsHeight
                }
                ActiviteListView {
                    model: ddb.getPagesByMatiereAndActivite(_comboBoxSelectMatiere.currentText, 1)
                    commonHeight: 30
                    headerText: "Exercices"
                    headerColor: "orange"
                    height: activitesColumn.activiteListViewsHeight
                }
             }
        }
    }


}
}