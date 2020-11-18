import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: item

    property QtObject classeur

    width: 600
    height: 500
    objectName: "ClasseurLayout"

    CasTest {
        property var lv
        property var header

        function initPre() {
            let mat = fk.f("matiere", {
                "bgColor": "red"
            });
            let ac1 = fk.f("activite", {
                "matiere": mat.id,
                "nom": "Evaluations"
            });
            let p1 = fk.f("page", {
                "activite": ac1.id,
                "titre": "un titre"
            });
            let p2 = fk.f("page", {
                "activite": ac1.id,
                "titre": "un titre2"
            });
            let p3 = fk.f("page", {
                "activite": ac1.id,
                "titre": "un titre3"
            });
            classeurid.setCurrentMatiere(mat.id);
            params["model"] = classeurid.pagesParActivite[0];
            params["width"] = 300;
        }

        function initPost() {
            lv = findChild(tested, "lv");
            header = findChild(tested, "header");
        }

        function test_header() {
            compare(header.label.text, "Evaluations");
        }

        function test_new_page_via_header() {
            compare(lv.count, 3);
            mousePress(header.mousearea, 1, 1, Qt.RightButton);
            tested.model = classeurid.pagesParActivite[0];
            compare(lv.count, 4);
        }

        function test_right_click_show_move() {
            let dp = tested.deplacePage;
            verify(!dp.visible);
            mousePress(lv.itemAtIndex(0), undefined, undefined, Qt.RightButton);
            verify(dp.visible);
        }

        name: "ActiviteRectangle"
        testedNom: "qrc:/qml/matiere/ActiviteRectangle.qml"
        params: {
            "model": []
        }
    }

    classeur: Classeur {
        id: classeurid

        annee: 2019
    }

}
