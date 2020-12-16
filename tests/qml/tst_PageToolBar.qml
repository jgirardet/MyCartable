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
            wait(100); //image is async
            compare_new_section("ImageSection");
        }

        function test_newimagevide() {
            mouseClick(newimagevide);
            let ct = newimagevide.action.dialog.contentItem;
            mouseClick(ct, ct.width - 5, ct.height - 5, Qt.LeftButton, Qt.NoModifier, 50);
            compare_new_section("ImageSection");
        }

        function test_new_operation_data() {
            return [{
                "tag": "AdditionSection",
                "string": "23+3"
            }, {
                "tag": "SoustractionSection",
                "string": "23-3"
            }, {
                "tag": "MultiplicationSection",
                "string": "5*2"
            }, {
                "tag": "DivisionSection",
                "string": "2/1"
            }];
        }

        function test_new_operation(data) {
            mouseClick(newoperation);
            newoperation.action.dialog.contentItem.text = data.string;
            newoperation.action.dialog.accept();
            compare_new_section(data.tag);
        }

        function test_newtableau() {
            mouseClick(newtableau);
            newtableau.action.dialog.accept();
            compare_new_section("TableauSection");
        }

        function test_removepage_confirmation_not_empty() {
            mouseClick(removepage);
            removepage.action.dialog.accept();
            removepage.action.dialog.confirmation.accept();
            compare(fk.getItem("Page", page.id), {
            });
        }

        function test_removepage_empty() {
            page = fk.f("page", {
            });
            pageC = th.getBridgeInstance(classeurid, "Page", page.id);
            classeurid.setPage(pageC.id);
            tested.page = pageC;
            mouseClick(removepage);
            removepage.action.dialog.accept();
            compare(fk.getItem("Page", page.id), {
            });
        }

        name: "PageToolBar"
        testedNom: "qrc:/qml/page/PageToolBar.qml"
        params: {
        }
    }

}
