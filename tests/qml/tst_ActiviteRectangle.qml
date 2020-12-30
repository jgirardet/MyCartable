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
        // doit etre dernier

        property var lv
        property var header
        property var p2
        property var p4
        property var actobj

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
            p2 = fk.f("page", {
                "activite": ac1.id,
                "titre": "un titre2"
            });
            let p3 = fk.f("page", {
                "activite": ac1.id,
                "titre": "un titre3"
            });
            p4 = fk.f("page", {
                "activite": ac1.id,
                "titre": "un titre ittre a ralonge hyper grnad comme c pas permis",
                "created": "1111-01-01T00:00:00"
            });
            classeur.annee = 2019;
            classeurid.setCurrentMatiere(mat.id);
            actobj = classeurid.currentMatiere.activites[0];
            params["activite"] = actobj;
            params["width"] = 300;
        }

        function initPost() {
            lv = findChild(tested, "lv");
            header = findChild(tested, "header");
            wait(50);
        }

        function test_header() {
            compare(header.label.text, "Evaluations");
        }

        function test_new_page_via_header() {
            compare(lv.count, 4);
            mousePress(header.mousearea, 1, 1, Qt.RightButton);
            compare(lv.count, 5);
        }

        function test_right_click_show_move() {
            let dp = tested.deplacePage;
            verify(!dp.visible);
            mousePress(lv.itemAtIndex(0), undefined, undefined, Qt.RightButton);
            verify(dp.visible);
        }

        function test_page_click() {
            let but = tested.pages.itemAtIndex(2);
            mouseClick(but);
            tryCompare(classeurid.page, "titre", but.contentItem.text);
        }

        function test_page_button_move_on_hovered() {
            // bien veiler à p4 == index 3 (date)
            let but = tested.pages.itemAtIndex(3);
            verify(but.contentItem.truncated);
            mouseMove(but, 1, 1);
            verify(!but.contentItem.truncated); // animation is running
        }

        function test_page_button_background() {
            let but = tested.pages.itemAtIndex(3);
            compare(but.background.border.width, 0);
            fuzzyCompare(but.background.color, "#cdd0d3", 0);
            mouseMove(but, 1, 1);
            compare(but.background.border.width, 3);
        }

        name: "ActiviteRectangle"
        testedNom: "qrc:/qml/matiere/ActiviteRectangle.qml"
        params: {
            "model": []
        }
    }

    classeur: Classeur {
        id: classeurid
    }

}
