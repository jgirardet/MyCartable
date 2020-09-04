import ".."
import Qt.labs.settings 1.0
import QtQuick 2.15

Item {
    id: item

    width: 200
    height: 200

    ListModel {
        //    ListElement {
        //        page: {"é"}
        //        cost: 2.45
        //    }

        id: pageModel

        property int lastPosition: 0

        signal modelReset()
    }

    CasTest {

        function initPre() {
        }

        function initPreCreate() {
            ddb.pageModel = pageModel;
        }

        function initPost() {
        }

        function test_init() {
        }

        function test_buzyindicator() {
            var baseItem = tested.contentItem.children[1];
            verify(baseItem.enabled);
            uiManager.buzyIndicator = true;
            verify(!baseItem.enabled);
        }

        function test_show_toast() {
            var toast = findChild(tested, "toast");
            verify(!toast.visible);
            uiManager.sendToast("blabla");
            verify(toast.visible);
            compare(toast.msg, "blabla");
        }

        name: ""
        testedNom: "qrc:/qml/main.qml"
        params: {
        }
    }

}
