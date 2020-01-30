import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12

Rectangle {
    id: base
    color: "yellow"
    property QtObject ddb

    ColumnLayout {
        id : activitesColumn
        anchors.fill: parent
        spacing: 5

        Rectangle {
            id: matiereSelect
            objectName : "matiereSelect"
            Layout.preferredHeight: ddb.getLayoutSizes("preferredHeaderHeight")
            Layout.minimumHeight: Layout.preferredHeight
            Layout.maximumHeight: Layout.preferredHeight
            Layout.fillWidth: true

            MatiereComboBox {
                id: _comboBoxSelectMatiere
                objectName: "_comboBoxSelectMatiere"
                model: base.ddb.matieresListNom
                currentIndex: base.ddb.getMatiereIndexFromId(database.currentMatiere)
                onActivated: base.ddb.setCurrentMatiereFromIndex(index)
            }


        }

        ActiviteRectangle {
            headerText: "Leçons"
            headerColor: "orange"
            ddb: base.ddb
            model: base.ddb.lessonsList
        }
        ActiviteRectangle {
            headerText: "Exercices"
            headerColor: "orange"
            ddb: base.ddb
            model: base.ddb.exercicesList
        }

        ActiviteRectangle {
            headerText: "Evaluations"
            headerColor: "orange"
            ddb: base.ddb
            model: base.ddb.evaluationsList
        }

     }
}
