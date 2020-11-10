import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: item

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
            ddb.anneeActive = 2018;
        }

        function test_init() {
            compare(ddb.recentsModel, tested.model);
        }

        function test_count() {
            compare(tested.count, 2);
        }

        name: "RecentsRectangle"
        testedNom: "qrc:/qml/matiere/RecentsRectangle.qml"
        params: {
        }
    }

}
