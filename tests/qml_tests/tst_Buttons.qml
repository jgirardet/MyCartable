import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/actions"

Item {
    id: item

    width: 200
    height: 200

    Buttons.BaseButton {
        id: basebutton

        action: PageActions.BasePageAction {
        }

    }

    CasTest {
        // enabled
        //        function test_basebutton() {
        //            ddb.currentPage = 0;
        //            ddb.currentPage = 0;
        //            ddb.currentPage = 0;
        //            print(basebutton.enabled);
        //            compare(basebutton.enabled, false);
        //            ddb.currentPage = 1;
        //            compare(tested.enabled, true);
        //        }
        //        function test_hovered() {
        //            // disabled
        //            ddb.currentPage = 0;
        //            compare(tested.visible, false);
        //            compare(tested.ToolTip.visible, false);
        //            compare(tested.background.color, ddb.colorPageToolBar); // disabled
        //            //enabled
        //            ddb.currentPage = 1;
        //            // active
        //            compare(tested.background.color, ddb.colorPageToolBar);
        //            //hovered
        //            mouseMove(tested, 1, 1);
        //            compare(tested.ToolTip.visible, true);
        //            compare(tested.background.color, "#838383"); // hovered
        //        }

        function initPre() {
        }

        function initPreCreate() {
        }

        function initPost() {
        }

        name: "Buttons"
        testedNom: "qrc:/qml/actions/Buttons.qml"
        params: {
            "icon.source": "qrc:///icons/newImageSection"
        }
    }

}
