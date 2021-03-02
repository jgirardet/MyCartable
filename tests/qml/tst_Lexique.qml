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
        //                "modified": Date()
        //                "modified": Date()
        //                "modified": Date()

        property var trad1
        property var trad2
        property var trad3
        property var tab
        property var gaucheI
        property var gaucheH
        property var droiteI
        property var droiteH

        function initPre() {
            database.setConfig("availables_locales", ['fr_FR', 'en_GB', 'it_IT', 'es_ES', 'de_DE']);
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
//
//        function test_init() {
//            compare(tab.columns, 2);
//            compare(tab.rows, 3);
//        }
//
//        function test_tableau_change_text() {
//            let bonjour = tab.itemAt(0, 1);
//            clickAndWrite(bonjour);
//            compare(bonjour.text, "bcd");
//        }
//
//        function test_header_tableau() {
//            let eng = gaucheH.text;
//            verify(eng.includes("British English"));
//            let fr = droiteH.text;
//            verify(fr.includes("français"));
//        }
//
//        function test_header_sort() {
//            mouseClick(droiteH);
//            compare(th.python("obj.sortColumn()", tab.model), 1);
//        }
//
//        function test_lexique_insert_lexon() {
//            clickAndWrite(gaucheI);
//            clickAndWrite(droiteI);
//            keyClick(Qt.Key_Return);
//            tryCompare(tested.tableau, "rows", 4);
//            compare(gaucheI.text, ""); //clear
//        }
//
//        function test_lexique_insert_navigation_data() {
//            return [{
//                "seq1": "",
//                "seq2": "",
//                "cote": "g",
//                "focus_after": "d",
//                "key": Qt.Key_Right,
//                "cursor": 0
//            }, {
//                "seq1": "",
//                "seq2": "",
//                "cote": "d",
//                "focus_after": "g",
//                "key": Qt.Key_Right,
//                "cursor": 0
//            }, {
//                "seq1": "b",
//                "seq2": "",
//                "cote": "g",
//                "focus_after": "g",
//                "key": Qt.Key_Right,
//                "cursor": 0
//            }, {
//                "seq1": "",
//                "seq2": "",
//                "cote": "d",
//                "focus_after": "g",
//                "key": Qt.Key_Left,
//                "cursor": 0
//            }, {
//                "seq1": "",
//                "seq2": "",
//                "cote": "g",
//                "focus_after": "d",
//                "key": Qt.Key_Left,
//                "cursor": 0
//            }, {
//                "seq1": "b",
//                "seq2": "",
//                "cote": "d",
//                "focus_after": "d",
//                "key": Qt.Key_Left,
//                "cursor": 1
//            }];
//        }
//
//        function test_lexique_insert_navigation(data) {
//            let cote = data.cote == "g" ? gaucheI : droiteI;
//            let focus_after = data.focus_after == "g" ? gaucheI : droiteI;
//            clickAndWrite(cote, data.seq1);
//            cote.cursorPosition = data.cursor;
//            keyClick(data.key);
//            verify(focus_after.activeFocus);
//        }
//
//        function test_filter() {
//            clickAndWrite(droiteI, "o,n");
//            tryCompare(tested.tableau, "rows", 1);
//        }
//
//        function test_show_header_if_filtered() {
//            clickAndWrite(droiteI, "z,z,z");
//            tryCompare(tested.tableau, "width", 0);
//            tryCompare(tested.header, "width", 600);
//        }
//
//        function test_toggle_matiere() {
//            mouseClick(tested.options.children[0]);
//            verify(tested.options.langues.itemAt(1).checked);
//            verify(tested.options.langues.itemAt(3).checked);
//            verify(!tested.options.langues.itemAt(4).checked);
//            compare(tested.tableau.columns, 2);
//            compare(tested.tableau.rows, 3);
//            //coche
//            mouseClick(tested.options.langues.itemAt(4));
//            tryCompare(tested.tableau, "columns", 3);
//            compare(tested.tableau.rows, 3);
//            //decoche
//            mouseClick(tested.options.langues.itemAt(1));
//            tryCompare(tested.tableau, "columns", 2);
//            compare(tested.tableau.rows, 3);
//        }
//
//        function test_remove_row() {
//            mouseClick(tested.tableau.itemAt(1, 0), 1, 1, Qt.MiddleButton);
//            tested.tableau.removeDialog.accept();
//            tryCompare(tested.tableau, "rows", 2);
//        }

        function test_quizz() {
            let trad4 = fk.f("traduction", {
                "lexon": trad1.lexon,
                "locale": "en_GB",
                "content": "hello"
            });
            let trad5 = fk.f("traduction", {
                "lexon": trad2.lexon,
                "locale": "fr_FR",
                "content": "au revoir"
            });
            let trad6 = fk.f("traduction", {
                "lexon": trad3.lexon,
                "locale": "en_GB",
                "content": "thanks"
            });
            //            tested.destroy();
            let lex = createObj(testedNom, {
            }, item);
            let qz = lex.lexique.quizz;
            mouseClick(lex.options.children[1]);
            let quizz = lex.options.quizz;
            compare(quizz.question.text, qz.question);
            compare(quizz.reponse.text, "");
            compare(qz.anteriorite.toString(), quizz.anteriorite.text)
            keyClick(Qt.Key_Return); // mauvaise reponse, verifie aussi le focus onOpen
            compare(quizz.reponse.text, "réponse: " + qz.reponse);
            qz.reponse = "bla"; //on triche pour le test
            keySequence("b,l,a");
            compare(qz.proposition, "bla");
            keyClick(Qt.Key_Return);
            compare(qz.score, 0);
            compare(qz.total, 1);
            //reinit pour question suivante
            compare(qz.proposition, "");
            compare(quizz.input.text, "");
            compare(quizz.reponse.text, "");
            // test changeanteriorite
            quizz.anteriorite.text = "1"
            compare(qz.score, 0) // donc reset
        }

        name: "Lexique"
        testedNom: "qrc:/qml/lexique/LexiqueLayout.qml"
    }

}
