import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: item

    width: 200
    height: 200

    Dialog {
        id: basedialog
    }

    Database {
        id: database
    }

    CasTest {
        function initPre() {
            basedialog.open();
            params = {
                "basePopup": basedialog
            };
        }

        function initPreCreate() {
        }

        function initPost() {
            tested.open();
        }

        function test_init() {
            compare(tested.nom, "");
            compare(tested.prenom, "");
            verify(!tested.alert.visible);
            Qt.colorEqual(tested.alert.color, "red");
        }

        function test_validation_nom() {
            tested.nom = "";
            tested.prenom = "aa";
            tested.accept();
            tryCompare(tested.alert, "visible", true);
        }

        function test_validation_prenom() {
            tested.nom = "aa";
            tested.prenom = "";
            tested.accept();
            tryCompare(tested.alert, "visible", true);
        }

        function test_validation_prenom_et_nom() {
            tested.nom = "";
            tested.prenom = "";
            tested.accept();
            tryCompare(tested.alert, "visible", true);
        }

        function test_cancel() {
            verify(basedialog.visible);
            tested.reject();
            tryCompare(basedialog, "visible", false);
        }

        function test_accept_valid() {
            compare(database.getConfig("user_set"), undefined);
            tested.nom = "aaa";
            tested.prenom = "bb";
            tested.accept();
            tryCompare(tested, "visible", false);
            compare(database.getConfig("nom"), "aaa");
            compare(database.getConfig("prenom"), "bb");
            compare(database.getConfig("user_set"), true);
        }

        name: "NewUser"
        testedNom: "qrc:/qml/configuration/NewUser.qml"
    }

}
