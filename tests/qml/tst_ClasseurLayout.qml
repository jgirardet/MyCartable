//import QtQuick.Controls 2.15

//import MyCartable 1.0
import QtQuick 2.15
import "qrc:/qml/layouts"

Item {
    id: item

    property var page

    width: 800
    height: 800

    CasTest {
        //            ddb.anneeActive = 2019;

        function initPre() {
            globus.annee = 2019;
            page = fk.f("page");
        }

        function initPost() {
            compare(tested.objectName, "ClasseurLayout");
            compare(tested.classeur.annee, 2019);
        }

        function test_init() {
        }

        function test_add_page_focus_titre() {
        }

        name: "ClasseurLayout"
        testedNom: "qrc:/qml/layouts/ClasseurLayout.qml"
    }

}
