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

        function test_buzyindicator() {
            verify(tested.mainItem.enabled);
            uiManager.buzyIndicator = true;
            verify(!tested.mainItem.enabled);
        }

        function test_show_toast() {
            verify(!tested.toast.visible);
            uiManager.sendToast("blabla");
            verify(tested.toast.visible);
            compare(tested.toast.msg, "blabla");
        }

        name: "Main"
        testedNom: "qrc:/qml/main.qml"
        params: {
        }
    }

}
