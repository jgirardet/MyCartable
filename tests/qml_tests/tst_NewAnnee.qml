import ".."
import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: item

    width: 200
    height: 200

    CasTest {
        //        ddb.currentUser
        //            verify(nu.visible);

        function initPre() {
        }

        function initPreCreate() {
            ddb.currentUser = {
            };
        }

        function initPost() {
            tested.open();
        }

        function test_init() {
            compare(tested.annee, "");
            compare(tested.classe, "");
            verify(!tested.alert.visible);
            Qt.colorEqual(tested.alert.color, "red");
        }

        function test_open_new_user_if_no_user() {
            var nu = findChild(tested, "newUserDialog");
            //            tryCompare(tested, "visible", true);
            verify(nu.visible);
        }

        function test_not_open_new_user_if_user() {
            tested.close();
            var nu = findChild(tested, "newUserDialog");
            nu.close();
            ddb.currentUser = {
                "nom": "bla"
            };
            tested.open();
            wait(10);
            tryCompare(nu, "visible", false);
        }

        function test_validation_nom() {
            tested.annee = "";
            tested.classe = "aa";
            tested.accept();
            tryCompare(tested.alert, "visible", true);
        }

        function test_validation_prenom() {
            tested.annee = "2021";
            tested.classe = "";
            tested.accept();
            tryCompare(tested.alert, "visible", true);
        }

        function test_validation_prenom_et_nom() {
            tested.annee = "";
            tested.classe = "";
            tested.accept();
            tryCompare(tested.alert, "visible", true);
        }

        function test_accept_valid() {
            tested.annee = "2021";
            tested.classe = "cm2";
            tested.accept();
            tryCompare(tested, "visible", false);
            compare(ddb._newAnnee, ["2021", "cm2"]);
        }

        name: "NewAnnee"
        testedNom: "qrc:/qml/configuration/NewAnnee.qml"
    }

}
