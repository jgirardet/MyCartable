import QtQuick  2.15
import QtQuick.Controls 2.15

Item {
    id: item

    width: 200
    height: 200

    CasTest {

        function test_init() {
            compare(ddb.recentsModel, tested.children[0].children[1].model);
        }

        name: "RecentsRectangle"
        testedNom: "qrc:/qml/matiere/RecentsRectangle.qml"
        params: {
        }
    }

}
