import QtQuick 2.14

Item {
    id: item

    width: 50
    height: 50

    CasTest {
        property var model

        function initPre() {
        }

        function initPreCreate() {
        }

        function initPost() {
            model = ddb.recentsModel[0];
            tested.model = model;
            tested.width = 50;
        }

        function test_init_and_text() {
            compare(model.titre, "professeur secret espoir clé discuter");
        }

        function test_move() {
            verify(tested.contentItem.truncated == true);
            mouseMove(tested);
            verify(tested.contentItem.truncated == false); // animation is running
        }

        function test_onclick() {
            ddb.currentPage = 999999;
            mouseClick(tested);
            verify(ddb.currentPage == model.id);
        }

        function test_bground() {
            verify(tested.background.border.width == 1);
            verify(Qt.colorEqual(tested.background.color, model.matiereBgColor));
            mouseMove(tested);
            verify(tested.background.border.width == 3);
        }

        name: "PageButton"
        testedNom: "qrc:/qml/divers/PageButton.qml"
    }

}
