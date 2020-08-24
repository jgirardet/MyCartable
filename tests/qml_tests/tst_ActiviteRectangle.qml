import QtQuick 2.14

Item {
    id: item

    width: 200
    height: 200

    CasTest {
        //      tested.width = item.width //fix le problème deLayout.fillWidth
        //      tested.height = item.height //fix le problème deLayout en test
        //    function test_header_click() {
        //      mouseClick(header, 0, 0, Qt.RightButton)
        //      compare(ddb._newPage, tested.model.id)
        //    }
        //    function test_some_properties() {
        //    }
        //    function test_lv_item() {
        //      var zero = lv.contentItem.children[0]
        ////      ddb.currentPage = 0
        //      compare(zero.contentItem.text, 'sauter course envoyer sympa boîte')
        //      compare(zero.contentItem.verticalAlignment, Text.AlignVCenter)
        //      compare(Qt.colorEqual(zero.contentItem.color, "white"), true)
        //      compare(zero.height, 30)
        //    }
        //    function test_click_on_item() {
        ////    var zero = lv.contentItem.children[0]
        ////      lv.forceLayout()
        ////    print(zero)
        ////      mouseClick(zero)
        ////     compare(ddb.currentPage, 22)
        //    }

        property var lv
        property var header

        function initPreCreate() {
            params["model"] = ddb.pagesParSection[2];
        }

        function initPost() {
            lv = findChild(tested, "lv");
            header = findChild(tested, "header");
        }

        function test_header() {
            compare(header.label.text, "Evaluations");
        }

        function test_new_page_via_header() {
            ddb._newPage = "xx";
            mouseClick(header.mousearea, 0, 0, Qt.RightButton);
            compare(ddb._newPage, 9);
        }

        name: "ActiviteRectangle"
        testedNom: "qrc:/qml/matiere/ActiviteRectangle.qml"
        params: {
            "model": []
        }
    }

}
