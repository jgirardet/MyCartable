import QtQuick 2.12
import QtQuick.Controls 2.12

        Rectangle {
            id: matiereRectangle
            color: "yellow"
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
                    objectName : "matiereSelect"
                    height: root.headersHeight
                    width: root.lateralsColumnWidth
                    MatiereComboBox {
                        id: _comboBoxSelectMatiere
                        objectName: "_comboBoxSelectMatiere"
                        model: database.matieresListNom
                        currentIndex: database.getMatiereIndexFromId(database.currentMatiere)
                        onActivated:database.setCurrentMatiereFromIndex(index)
                    }


                }

                ActiviteListView {
                    id: _listViewLessons
                    objectName: "_listViewLessons"
                    model: database.getPagesByMatiereAndActivite(_comboBoxSelectMatiere.currentText, 0)
//                    model: database.getPagesByMatiereAndActivite(_comboBoxSelectMatiere.currentText, 0)
                    commonHeight: 30
                    headerText: "Leçons"
                    headerColor: "pink"
                    height: activitesColumn.activiteListViewsHeight
                }
                ActiviteListView {
                    id: _listViewExercices
                    objectName: "_listViewExercices"
                    model: database.getPagesByMatiereAndActivite(_comboBoxSelectMatiere.currentText, 1)
                    commonHeight: 30
                    headerText: "Exercices"
                    headerColor: "orange"
                    height: activitesColumn.activiteListViewsHeight
                }
             }
        }