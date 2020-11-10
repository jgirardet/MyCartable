import QtQuick 2.15

Item {
    id: item

    width: 200
    height: 200

    Component {
        id: red

        Rectangle {
            color: "red"
        }

    }

    Component {
        id: blue

        Rectangle {
            color: "blue"
        }

    }

    Component {
        id: green

        Rectangle {
            color: "green"
        }

    }

    CasTest {
        function initPre() {
            params = {
                "componentKeys": {
                    "red": red,
                    "blue": blue,
                    "green": green
                },
                "initModel": [{
                    "type": "red"
                }, {
                    "type": "red"
                }, {
                    "type": "green"
                }, {
                    "type": "blue"
                }],
                "anchors.fill": item
            };
        }

        function initPreCreate() {
        }

        function initPost() {
            // wait everything loaded
            tryCompare(tested.items.get(0), "width", 50);
        }

        function test_init() {
            compare(tested.count, 4);
        }

        function test_flip() {
            compare(tested.items.get(2).width, 50);
            tested.flip();
            tryCompare(tested.items.get(2), "height", 50);
        }

        function test_order() {
            fuzzyCompare(tested.items.get(0).item.color, "red", 0);
            fuzzyCompare(tested.items.get(1).item.color, "red", 0);
            fuzzyCompare(tested.items.get(2).item.color, "green", 0);
            fuzzyCompare(tested.items.get(3).item.color, "blue", 0);
        }

        function test_horizontal_size() {
            compare(tested.items.get(0).width, 50);
            compare(tested.items.get(0).height, 200);
        }

        function test_verticall_size() {
            tested.flip();
            tryCompare(tested.items.get(0), "width", 200);
            compare(tested.items.get(0).height, 50);
            compare(tested.items.get(1).width, 200);
            compare(tested.items.get(1).height, 50);
        }

        name: "SplitLayout"
        testedNom: "qrc:/qml/layouts/SplitLayout.qml"
        params: {
        }
    }

}
