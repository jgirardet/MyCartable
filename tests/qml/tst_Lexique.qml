import MyCartable 1.0
import QtQuick 2.15

Item {
    id: item

    width: 1000
    height: 600

    Database {
        id: database
    }

    CasTest {
        property var trad1
        property var trad2
        property var trad3
        property var tab
        property var gaucheI
        property var gaucheH
        property var droiteI
        property var droiteH

        function initPre() {
            database.setConfig("availables_locales", ['fr_FR', 'en_GB', 'it_IT']);
            database.setConfig("actives_locales", ['fr_FR', 'en_GB']);
            trad1 = fk.f("traduction", {
                "locale": "fr_FR",
                "content": "bonjour"
            });
            trad2 = fk.f("traduction", {
                "locale": "en_GB",
                "content": "goodbye"
            });
            trad3 = fk.f("traduction", {
                "locale": "fr_FR",
                "content": "merci"
            });
        }

        function initPost() {
            tab = tested.tableau;
            tryCompare(tab, "rows", 3);
            tryCompare(tab, "width", database.getConfig("lexiqueColumnWidth") * 2);
            gaucheI = tested.inserter.items.itemAt(0);
            droiteI = tested.inserter.items.itemAt(1);
            gaucheH = tested.header.contentItem.children[0];
            droiteH = tested.header.contentItem.children[1];
        }

        function test_init() {
            compare(tab.columns, 2);
            compare(tab.rows, 3);
        }

        function test_tableau_itemAt_and_content_text() {
            compare(tab.itemAt(0, 0).text, "");
            compare(tab.itemAt(0, 1).text, trad1.content);
            compare(tab.itemAt(1, 0).text, trad2.content);
            compare(tab.itemAt(1, 1).text, "");
            compare(tab.itemAt(2, 0).text, "");
            compare(tab.itemAt(2, 1).text, trad3.content);
        }

        function test_tableau_change_text() {
            let bonjour = tab.itemAt(0, 1);
            clickAndWrite(bonjour);
            compare(bonjour.text, "bcd");
        }

        function test_header_tableau() {
            let eng = gaucheH.text;
            verify(eng.includes("British English"));
            let fr = droiteH.text;
            verify(fr.includes("français"));
        }

        function test_header_sort() {
            mouseClick(droiteH);
            compare(th.python("obj.sortColumn()", tab.model), 1);
        }

        function test_lexique_insert_lexon() {
            clickAndWrite(gaucheI);
            clickAndWrite(droiteI);
            keyClick(Qt.Key_Return);
            tryCompare(tested.tableau, "rows", 4);
            compare(gaucheI.text, ""); //clear
        }

        function test_lexique_insert_navigation_data() {
            return [{
                "seq1": "",
                "seq2": "",
                "cote": "g",
                "focus_after": "d",
                "key": Qt.Key_Right,
                "cursor": 0
            }, {
                "seq1": "",
                "seq2": "",
                "cote": "d",
                "focus_after": "g",
                "key": Qt.Key_Right,
                "cursor": 0
            }, {
                "seq1": "b",
                "seq2": "",
                "cote": "g",
                "focus_after": "g",
                "key": Qt.Key_Right,
                "cursor": 0
            }, {
                "seq1": "",
                "seq2": "",
                "cote": "d",
                "focus_after": "g",
                "key": Qt.Key_Left,
                "cursor": 0
            }, {
                "seq1": "",
                "seq2": "",
                "cote": "g",
                "focus_after": "d",
                "key": Qt.Key_Left,
                "cursor": 0
            }, {
                "seq1": "b",
                "seq2": "",
                "cote": "d",
                "focus_after": "d",
                "key": Qt.Key_Left,
                "cursor": 1
            }];
        }

        function test_lexique_insert_navigation(data) {
            let cote = data.cote == "g" ? gaucheI : droiteI;
            let focus_after = data.focus_after == "g" ? gaucheI : droiteI;
            clickAndWrite(cote, data.seq1);
            cote.cursorPosition = data.cursor;
            keyClick(data.key);
            verify(focus_after.activeFocus);
        }

        function test_filter() {
            clickAndWrite(droiteI, "o,n");
            tryCompare(tested.tableau, "rows", 1);
        }

        function test_show_header_if_filtered() {
            clickAndWrite(droiteI, "z,z,z");
            tryCompare(tested.tableau, "width", 0);
            tryCompare(tested.header, "width", 600);
        }

        function test_toggle_matiere() {
            verify(tested.options.items.itemAt(0).checked);
            verify(tested.options.items.itemAt(1).checked);
            verify(!tested.options.items.itemAt(2).checked);
            compare(tested.tableau.columns, 2);
            compare(tested.tableau.rows, 3);
            //coche
            mouseClick(tested.options.items.itemAt(2));
            tryCompare(tested.tableau, "columns", 3);
            compare(tested.tableau.rows, 3);
            //decoche
            mouseClick(tested.options.items.itemAt(0));
            tryCompare(tested.tableau, "columns", 2);
            compare(tested.tableau.rows, 3);
        }

        function test_remove_row() {
            mouseClick(tested.tableau.itemAt(1, 0), 1, 1, Qt.MiddleButton);
            tested.tableau.removeDialog.accept();
            tryCompare(tested.tableau, "rows", 2);
        }

        name: "Lexique"
        testedNom: "qrc:/qml/lexique/LexiqueLayout.qml"
    }

}
