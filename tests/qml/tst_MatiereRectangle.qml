import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: item

    property QtObject classeur

    width: 200
    height: 200
    objectName: "ClasseurLayout" // pour test deplace page

    CasTest {
        property Item chooser
        property var mat0
        property var mat1
        property var ac0
        property var ac1

        function initPre() {
            params = {
                "classeur": classeur
            };
            mat0 = fk.f("matiere", {
                "nom": "Maths",
                "groupe": 2019
            });
            mat1 = fk.f("matiere", {
                "nom": "Greque",
                "groupe": 2019
            });
            ac0 = fk.f("activite", {
                "nom": "ac0",
                "matiere": mat0.id
            });
            ac1 = fk.f("activite", {
                "nom": "ac1",
                "matiere": mat0.id
            });
            classeur.annee = 2019;
        }

        function initPost() {
            chooser = tested.chooser;
        }

        function test_init() {
            compare(chooser, tested.chooser);
        }

        function test_matiere_combox() {
            compare(chooser.currentIndex, 0);
            compare(chooser.contentItem.text, "Maths");
            mouseClick(chooser, 50);
            keyClick(Qt.Key_Down);
            keyClick(Qt.Key_Return);
            compare(chooser.currentIndex, 1);
            compare(chooser.contentItem.text, "Greque");
            fuzzyCompare(chooser.background.color, mat1.bgColor, 0);
        }

        function test_combo_popup() {
            chooser.popup.open();
            var le_un = chooser.popup.contentItem.itemAtIndex(0);
            compare(le_un.contentItem.text, mat0.nom);
            fuzzyCompare(le_un.contentItem.color, mat0.fgColor, 0);
            fuzzyCompare(le_un.background.color, mat0.bgColor, 0);
        }

        function test_classeur_interaction() {
            compare(chooser.model, classeur.matieresDispatcher.matieresList);
            compare(chooser.currentIndex, classeur.currentMatiereIndex);
            compare(chooser.currentIndex, 0);
            classeur.setCurrentMatiere(1);
            compare(chooser.currentIndex, 1);
            chooser.activated(0);
            compare(chooser.currentIndex, classeur.currentMatiereIndex);
            compare(classeur.currentMatiereIndex, 0);
        }

        function test_activite_rectangle() {
            chooser.activated(0);
            compare(tested.activites.model, classeur.currentMatiere.activites);
            compare(tested.activites.count, 2);
        }

        // testé ici car necessite  2 activités différents
        function test_deplace_page() {
            let page = fk.f("page", {
                "activite": ac0.id
            });
            chooser.activated(0);
            let ac_rec0 = tested.activites.itemAtIndex(0);
            let ac_rec1 = tested.activites.itemAtIndex(1);
            compare(ac_rec0.pages.count, 1);
            compare(ac_rec1.pages.count, 0);
            mouseClick(ac_rec0.pages.itemAtIndex(0), undefined, undefined, Qt.RightButton);
            let bt0 = ac_rec0.deplacePage.buttons.itemAt(0);
            mouseMove(bt0, 1, 1);
            mouseClick(bt0.repActivites.itemAt(1));
            ac_rec0 = tested.activites.itemAtIndex(0);
            ac_rec1 = tested.activites.itemAtIndex(1);
            compare(ac_rec0.pages.count, 0);
            compare(ac_rec1.pages.count, 1);
        }

        name: "MatiereRectangle"
        testedNom: "qrc:/qml/matiere/MatiereRectangle.qml"
    }

    classeur: Classeur {
        id: classeur
    }

}
