import ".."
import QtQuick 2.15

Item {
    id: item

    width: 200
    height: 200

    CasTest {
        //            wait(3000);

        property var newtext
        property var newimage
        property var newequation
        property var newoperation
        property var newtableau
        property var removepage
        property var exportodt
        property var exportpdf

        function initPre() {
        }

        function initPreCreate() {
            ddb.currentPage = 1;
            ddb.pageModel = {
                "count": 4
            };
        }

        function initPost() {
            var toolbar = tested.children[0].children[0].children[0].children[0].children[0];
            newtext = toolbar.children[0];
            newimage = toolbar.children[1];
            newequation = toolbar.children[2];
            newoperation = toolbar.children[3];
            newtableau = toolbar.children[4];
            removepage = toolbar.children[5];
            exportodt = toolbar.children[6];
            exportpdf = toolbar.children[7];
        }

        function test_init() {
            verify(tested.visible);
        }

        function test_newtext() {
            mouseClick(newtext);
            compare(ddb._addSection, [1, {
                "classtype": "TextSection",
                "position": 4
            }]);
        }

        function test_newequation() {
            mouseClick(newequation);
            compare(ddb._addSection, [1, {
                "classtype": "EquationSection",
                "position": 4
            }]);
        }

        function test_newimage() {
            mouseClick(newimage);
            newimage.action.dialog.accept();
            compare(ddb._addSection, [1, {
                "path": "",
                "classtype": "ImageSection",
                "position": 4
            }]);
        }

        function test_newoperation() {
            mouseClick(newimage);
            newoperation.action.dialog.contentItem.text = "45*23";
            newoperation.action.dialog.accept();
            compare(ddb._addSection, [1, {
                "string": "45*23",
                "classtype": "OperationSection",
                "position": 4
            }]);
        }

        function test_newtableau() {
            mouseClick(newimage);
            newtableau.action.dialog.accept();
            compare(ddb._addSection, [1, {
                "lignes": 1,
                "colonnes": 1,
                "classtype": "TableauSection",
                "position": 4,
                "modele": ""
            }]);
        }

        function test_removepage() {
            mouseClick(removepage);
            compare(ddb._removePage, [1]);
        }

        function test_exportpdf() {
            mouseClick(exportpdf);
            compare(ddb._exportToPDF, ["called"]);
        }

        function test_exportodt() {
            mouseClick(exportodt);
            compare(ddb._exportToOdt, ["called"]);
        }

        name: "PageToolBar"
        testedNom: "qrc:/qml/page/PageToolBar.qml"
        params: {
        }
    }

}
