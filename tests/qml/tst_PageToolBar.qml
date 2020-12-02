import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Window 2.15

Item {
    id: item

    width: 800
    height: 200

    Classeur {
        id: classeurid
    }

    CasTest {
        //            ddb.currentPage = page.id; // to make toolbar visible
        //            mouseClick(newimage.action.dialog.contentItem, 200, 100);
        //            compare(args[0], page.id);
        //            compare(args[1], {
        //                "width": 1280,
        //                "height": 1200,
        //                "classtype": "ImageSectionVide",
        //                "position": 3
        //            });

        id: testcase

        property var newtext
        property var newimage
        property var newimagevide
        property var newequation
        property var newoperation
        property var newtableau
        property var newfrise
        property var removepage
        property var exportodt
        property var exportpdf
        property var page
        property var pageC

        function initPre() {
            page = fk.f("page", {
            });
            for (const i of Array(3).keys()) {
                fk.f("section", {
                    "page": page.id
                });
            }
            pageC = th.getBridgeInstance(classeurid, "Page", page.id);
            params = {
                "page": pageC
            };
            classeurid.setPage(pageC.id);
        }

        function initPost() {
            var toolbar = tested.children[0].children[0].children[0].children[0].children[0];
            newtext = toolbar.children[0];
            newimage = toolbar.children[1];
            newimagevide = toolbar.children[2];
            newequation = toolbar.children[3];
            newoperation = toolbar.children[4];
            newtableau = toolbar.children[5];
            newfrise = toolbar.children[6];
            removepage = toolbar.children[7];
            exportodt = toolbar.children[8];
            exportpdf = toolbar.children[9];
        }

        function test_init() {
            verify(tested.visible);
            compare(tested.page.id, page.id);
            compare(tested.page.model.count, 3);
        }

        function compare_new_section(classtype) {
            let sections = fk.getSet("Page", page.id, "sections");
            compare(sections.length, 4);
            let section = sections[3];
            compare(section.position, 3);
            compare(section.classtype, classtype);
            return section;
        }

        function test_simple_new_section_data() {
            return [{
                "tag": "newtext",
                "classtype": "TextSection"
            }, {
                "tag": "newequation",
                "classtype": "EquationSection"
            }, {
                "tag": "newfrise",
                "classtype": "FriseSection"
            }];
        }

        function test_simple_new_section(data) {
            let button = testcase[data.tag];
            mouseClick(button);
            compare_new_section(data.classtype);
        }

        function test_mocked_data() {
            return [{
                "tag": "exportpdf",
                "fnName": "exportToPDF"
            }, {
                "tag": "exportodt",
                "fnName": "exportToOdt"
            }];
        }

        function test_mocked(data) {
            let button = testcase[data.tag];
            th.mock(data.fnName);
            mouseClick(button);
            verify(th.mock_called(data.fnName));
            th.unmock(data.fnName);
        }

        function test_newimage() {
            mouseClick(newimage);
            newimage.action.dialog.folder = "assets";
            mouseDoubleClickSequence(newimage.action.dialog.contentItem, 150, 150, Qt.LeftButton, Qt.NoModifier, 50);
            //            print(JSON.stringify(fk.getSet("Page", page.id, "sections")));
            compare_new_section("ImageSection");
        }

        function test_newimagevide() {
            mouseClick(newimagevide);
            let ct = newimagevide.action.dialog.contentItem;
            mouseClick(ct, ct.width - 5, ct.height - 5, Qt.LeftButton, Qt.NoModifier, 50);
            let newSec = compare_new_section("ImageSection");
        }

        function test_newoperation() {
            th.mock("addSection");
            mouseClick(newimage);
            newoperation.action.dialog.contentItem.text = "45*23";
            newoperation.action.dialog.accept();
            let args = th.mock_call_args_list('addSection')[0];
            compare(args[0], page.id);
            compare(args[1], {
                "string": "45*23",
                "classtype": "OperationSection",
                "position": 3
            });
            th.unmock("addSection");
        }

        function test_newtableau() {
            th.mock("addSection");
            mouseClick(newimage);
            newtableau.action.dialog.accept();
            let args = th.mock_call_args_list('addSection')[0];
            compare(args[0], page.id);
            compare(args[1], {
                "lignes": 1,
                "colonnes": 1,
                "classtype": "TableauSection",
                "position": 3,
                "modele": ""
            });
            th.unmock("addSection");
        }

        function test_removepage() {
            mouseClick(removepage);
            compare(fk.getItem("Page", page.id), {
            });
        }

        name: "PageToolBar"
        testedNom: "qrc:/qml/page/PageToolBar.qml"
        params: {
        }
    }

}
