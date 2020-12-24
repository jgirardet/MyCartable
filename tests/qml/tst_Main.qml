import Qt.labs.settings 1.0
import QtQuick 2.15

Item {
    id: item

    width: 200
    height: 200

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
            compare(tested.mainItem.layouts, uiManager.mainLayouts);
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
