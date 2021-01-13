import QtQuick 2.15

Item {
    id: item

    width: 600
    height: 600

    CasTest {
        property var trad1
        property var trad2
        property var trad3
        property var tab
        property var bonjour

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
            bonjour = tab.itemAt(0, 1);
        }

        function test_init() {
            compare(tab.columns, 2);
            compare(tab.rows, 3);
            compare(tab.width, tested.width);
            compare(tab.width, item.width);
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
            clickAndWrite(bonjour);
            compare(bonjour.text, "bcd");
        }

        name: "Lexique"
        testedNom: "qrc:/qml/lexique/LexiqueLayout.qml"
    }

}
