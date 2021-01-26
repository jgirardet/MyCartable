import MyCartable 1.0
import QtQuick 2.15

Item {
    id: item

    width: 600
    height: 600

    Classeur {
        id: classeur_id
    }

    CasTest {
        property var pageD
        property QtObject page
        property QtObject classeur

        function initPre() {
            pageD = fk.f("page", {
                "titre": "le titre"
            });
            let annee = fk.f("annee", {
                "id": 2009
            });
            classeur_id.annee = 2009;
            page = th.getBridgeInstance(classeur_id, "Page", pageD.id);
            page.undoStack = classeur_id.undoStack;
            params = {
                "page": page,
                "anchors.fill": item
            };
        }

        function initPost() {
        }

        function test_init() {
            compare(tested.page, page);
        }

        function test_titre_init() {
            tested.titre.text = "le titre";
        }

        function test_titre_focus_if_emplty() {
            let pD = fk.f("page", {
                "titre": "aaa"
            });
            let p = th.getBridgeInstance(item, "Page", pD.id);
            tested.titre.focus = false;
            tested.page = p; // not empty text
            compare(tested.titre.focus, false);
            compare(tested.titre.text, "aaa");
            tested.page = null;
            p.titre = "";
            tested.page = p; // not empty text
            compare(tested.titre.focus, true);
            compare(tested.titre.text, "");
        }

        function test_titre_update_titre() {
            clickAndWrite(tested.titre);
            compare(tested.titre.text, "bcd");
            compare(dtb.getDB("Page", page.id).titre, "bcd");
        }

        function test_titre_add_sectionText_on_enter_but_no_other_section() {
            let pD = fk.f("page", {
                "titre": ""
            });
            let p = th.getBridgeInstance(classeur_id, "Page", pD.id);
            p.undoStack = classeur_id.undoStack;
            tested.page = p;
            mouseClick(tested.titre);
            keyClick(Qt.Key_Return);
            compare(p.model.count, 1);
        }

        function test_show_busy() {
            tryCompare(tested.busy, 'visible', false);
            tryCompare(tested.loaderps, "populated", true);
            tested.loaderps.populated = false;
            tryCompare(tested.busy, 'visible', true);
            tested.loaderps.populated = true;
            tryCompare(tested.busy, 'visible', false);
        }

        function test_rectangle_page_is_null() {
            tested.page = null;
            tryCompare(tested.loaderps, 'state', "");
            tryCompare(tested.loaderps, "populated", false);
            verify(!tested.loaderps.item);
            tryCompare(tested.busy, 'visible', false);
        }

        name: "PageRectangle"
        testedNom: "qrc:/qml/page/PageRectangle.qml"
    }

}
