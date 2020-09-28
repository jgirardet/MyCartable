import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: item

    width: 400
    height: 400

    CasTest {
        function initPreCreate() {
            fk.resetDB();
        }

        function initPost() {
        }

        function test_init() {
        }

        function initPre() {
        }

        params: {
        }
        testedNom: "qrc:/qml/sections/FriseSection.qml"
        name: "FriseSection"
    }

}
