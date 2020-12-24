import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: item

    property var classeur

    width: 200
    height: 200

    CasTest {
        function initPre() {
            let a = fk.f("annee", {
                "id": 2018
            });
            let gp = fk.f("groupeMatiere", {
                "annee": a.id
            });
            let m = fk.f("matiere", {
                "groupe": gp.id
            });
            let ac = fk.f("activite", {
                "matiere": m.id
            });
            let p1 = fk.f("page", {
                "created": "2018-12-12",
                "activite": ac.id
            });
            let p2 = fk.f("page", {
                "created": "2018-01-12",
                "activite": ac.id
            });
            classeur.annee = 2018;
            params = {
                "model": classeur.recents
            };
        }

        function init_post() {
        }

        function test_init() {
            compare(classeur.recents, tested.model);
        }

        function test_count() {
            compare(tested.count, 2);
        }

        function test_page_click() {
            wait(50);
            let but = tested.itemAtIndex(1);
            mouseClick(but);
            tryCompare(classeur.page, "titre", but.contentItem.text);
        }

        name: "RecentsRectangle"
        testedNom: "qrc:/qml/matiere/RecentsRectangle.qml"
        params: {
        }
    }

    classeur: Classeur {
        id: classeur
    }

}
