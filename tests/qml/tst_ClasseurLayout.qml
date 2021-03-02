import QtQuick 2.15
import "qrc:/qml/layouts"

Item {
    id: item

    width: 800
    height: 800

    CasTest {
        property var p1
        property var p2
        property var sec
        property var cl

        function initPre() {
            let mat = fk.f("matiere", {
                "groupe": 2019
            });
            let ac = fk.f("activite", {
                "matiere": mat.id
            });
            p1 = fk.f("page", {
                "activite": ac.id
            });
            sec = fk.f("textSection", {
                "page": p1.id
            });
            p2 = fk.f("page", {
                "activite": ac.id
            });
        }

        function initPost() {
            compare(tested.objectName, "ClasseurLayout");
            compare(tested.classeur.annee, 2019);
            cl = tested.classeur;
        }

        function test_init() {
        }

        function test_set_page() {
            //utilise pour explorer "binding broken" avce section required dans basepage delegate
            //enlevé depuis. Pas vraiment util du coup...
            cl.setPage(p1.id);
            tryCompare(tested.hamAndCheese.loaderps, "populated", true);
            cl.setPage(p2.id);
        }

        name: "ClasseurLayout"
        testedNom: "qrc:/qml/layouts/ClasseurLayout.qml"
    }

}
