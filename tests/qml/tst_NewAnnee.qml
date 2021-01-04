import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: item

    property var changerAnnee

    width: 200
    height: 200

    Database {
        id: database
    }

    CasTest {
        function initPre() {
            database.setConfig("user_set", true);
        }

        function initPreCreate() {
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
            tested.close();
            var nu = findChild(tested, "newUserDialog");
            nu.close();
            database.setConfig("user_set", false);
            tested.open();
            tryCompare(nu, "visible", true);
        }

        function test_not_open_new_user_if_user() {
            tested.close();
            var nu = findChild(tested, "newUserDialog");
            nu.close();
            database.setConfig("user_set", true);
            tested.open();
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
            //            wait(2000);
            tested.accept();
            //            wait(2000);
            tryCompare(tested, "visible", false);
            //            wait(2000);
            compare(database.getDB("Annee", 2021), {
                "id": 2021,
                "niveau": "cm2"
            });
        }

        name: "NewAnnee"
        testedNom: "qrc:/qml/configuration/NewAnnee.qml"
    }

    changerAnnee: Popup {
    }

}
