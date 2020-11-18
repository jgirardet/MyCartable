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
        function initPre() {
            page = fk.f("page");
            ddb.anneeActive = 2019;
        }

        function initPost() {
            compare(tested.objectName, "ClasseurLayout");
            compare(tested.classeur.annee, 2019);
        }

        function test_init() {
        }

        name: "ClasseurLayout"
        testedNom: "qrc:/qml/layouts/ClasseurLayout.qml"
    }

}
