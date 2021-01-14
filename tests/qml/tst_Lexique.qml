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
        //            wait(2000);
        //        function test_aaatableau_insert() {
        //            wait(2000);
        //        }
        //            tryCompare(tested, "width", item.width);
        //            wait(1000);
        //            mouseClick(tab.header.contentItem.children[0]);
        //            wait(1000);
        //            compare(th.python("obj.sortColumn()", tab.content.model), 0);
        //            wait(2000);

        property var trad1
        property var trad2
        property var trad3
        property var tab

        function initPre() {
            trad1 = fk.f("traduction", {
                "locale": "fr_FR",
                "content": "bonjour"
            });
            trad2 = fk.f("traduction", {
                "locale": "en_US",
                "content": "goodbye"
            });
            trad3 = fk.f("traduction", {
                "locale": "fr_FR",
                "content": "merci"
            });
        }

        function initPost() {
            tab = tested.tableau;
            tryCompare(tab.content, "rows", 3);
            tryCompare(tab, "width", database.getConfig("lexiqueColumnWidth") * 2);
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
            let eng = tab.header.contentItem.children[0].text;
            verify(eng.includes("ENGLISH"));
            let fr = tab.header.contentItem.children[1].text;
            verify(fr.includes("FRANÇAIS"));
        }

        function test_header_sort() {
            mouseClick(tab.header.contentItem.children[1]);
            compare(th.python("obj.sortColumn()", tab.content.model), 1);
        }

        function test_lexique_insert_lexon() {
            clickAndWrite(tested.inserter.items.itemAt(0));
            keyClick(Qt.Key_Return);
            tryCompare(tested.tableau.content, "rows", 4);
            compare(tested.inserter.items.itemAt(0).text, ""); //clear
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
            let gauche = tested.inserter.items.itemAt(0);
            let droite = tested.inserter.items.itemAt(1);
            let cote = data.cote == "g" ? gauche : droite;
            let focus_after = data.focus_after == "g" ? gauche : droite;
            clickAndWrite(cote, data.seq1);
            cote.cursorPosition = data.cursor;
            keyClick(data.key);
            verify(focus_after.activeFocus);
        }

        function test_filter() {
            let gauche = tested.inserter.items.itemAt(1);
            clickAndWrite(gauche, "o,n");
            tryCompare(tested.tableau, "rows", 1);
        }

        name: "Lexique"
        testedNom: "qrc:/qml/lexique/LexiqueLayout.qml"
    }

}
