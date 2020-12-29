import MyCartable 1.0
import Qt.labs.settings 1.0
import QtQuick 2.15

Item {
    id: item

    width: 200
    height: 200

    Database {
        id: database
    }

    CasTest {
        //            wait(1000);

        function initPre() {
        }

        function initPreCreate() {
        }

        function initPost() {
            tryCompare(tested, "visible", true);
        }

        function test_init() {
            compare(tested.mainItem.layouts, {
                "vide": {
                    "splittype": "vide",
                    "splittext": "",
                    "splitindex": 0,
                    "spliturl": "qrc:/qml/layouts/VideLayout.qml"
                },
                "classeur": {
                    "splittype": "classeur",
                    "splittext": "Classeur",
                    "splitindex": 1,
                    "spliturl": "qrc:/qml/layouts/ClasseurLayout.qml"
                }
            });
        }

        function cleanup() {
            tested.destroy();
        }

        name: "Main"
        testedNom: "qrc:/qml/main.qml"
        params: {
        }
    }

}
