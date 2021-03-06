import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: item

    width: 200
    height: 200

    CasTest {
        function initPre() {
            params = {
                "layouts": {
                    "red": {
                        "splittype": "red",
                        "splittext": "lered",
                        "spliturl": th.testPath("assets/splitlayout/SpRed.qml"),
                        "splitindex": 0
                    },
                    "blue": {
                        "splittype": "blue",
                        "splittext": "leblue",
                        "spliturl": th.testPath("assets/splitlayout/SpBlue.qml"),
                        "splitindex": 1
                    },
                    "green": {
                        "splittype": "green",
                        "splittext": "lergreen",
                        "spliturl": th.testPath("assets/splitlayout/SpGreen.qml"),
                        "splitindex": 2
                    },
                    "vide": {
                        "splittype": "vide",
                        "splittext": "levide",
                        "spliturl": "qrc:/qml/layouts/VideLayout.qml",
                        "splitindex": 3
                    }
                },
                "initDataModel": ["red", "red", "green", "blue"],
                "anchors.fill": item
            };
        }

        function initPost() {
            // wait everything loaded
            tryCompare(tested.items.get(0), "width", 50);
        }

        function test_init() {
            compare(tested.count, 4);
            compare(tested.get(0).splitType, "red");
            fuzzyCompare(tested.items.get(0).item.color, "red", 0);
            fuzzyCompare(tested.items.get(1).item.color, "red", 0);
            fuzzyCompare(tested.items.get(2).item.color, "green", 0);
            fuzzyCompare(tested.items.get(3).item.color, "blue", 0);
        }

        function test_loader_by_qrc_uri() {
            tested.append("vide");
            tryCompare(tested.get(4), "loaded", true);
            verify(tested.items.get(4).item.toString().includes("VideLayout_QMLTYPE"));
        }

        function test_loader_bad_comp() {
            tested.layouts = {
                "orange": {
                    "splittype": "orange",
                    "splittext": "leorange",
                    "spliturl": "erreur attendue, ne pas tenir compte",
                    "splitindex": 0
                }
            };
            tested.items.clear();
            tryCompare(tested, "count", 0);
            tested.append("orange");
            tryCompare(tested, "count", 0);
        }

        function test_append() {
            tested.append("green");
            tryCompare(tested.get(4), "loaded", true);
            fuzzyCompare(tested.get(0).item.color, "red", 0);
            fuzzyCompare(tested.get(1).item.color, "red", 0);
            fuzzyCompare(tested.get(2).item.color, "green", 0);
            fuzzyCompare(tested.get(3).item.color, "blue", 0);
            fuzzyCompare(tested.get(4).item.color, "green", 0);
        }

        function test_findSplitLoader() {
            compare(tested.findSplitLoader(tested.get(1).item.lebutton), tested.get(1));
            compare(tested.findSplitLoader(tested.get(2).item.lebutton), tested.get(2));
            compare(tested.findSplitLoader(tested.get(0)), tested.get(0));
            compare(tested.findSplitLoader(tested.get(0).item), tested.get(0));
        }

        function test_flip() {
            compare(tested.items.get(2).width, 50);
            tested.flip();
            tryCompare(tested.items.get(2), "height", 50);
        }

        function test_clear() {
            tested.clear();
            tryCompare(tested.items, "count", 1);
            wait(50);
            verify(tested.get(0).item.toString().includes("VideLayout_QMLTYPE"));
        }

        function test_get() {
            //get by item
            let but = tested.items.get(2).item.lebutton;
            compare(tested.get(but), tested.items.get(2));
            //get by index
            compare(tested.get(3), tested.items.get(3));
        }

        function test_insert() {
            tested.insert("green", 1);
            tryCompare(tested.get(1), "loaded", true);
            tryCompare(tested.get(1), "loaded", true);
            fuzzyCompare(tested.get(0).item.color, "red", 0);
            fuzzyCompare(tested.get(1).item.color, "green", 0);
            fuzzyCompare(tested.get(2).item.color, "red", 0);
            fuzzyCompare(tested.get(3).item.color, "green", 0);
            fuzzyCompare(tested.get(4).item.color, "blue", 0);
        }

        function test_pop() {
            tested.pop();
            compare(tested.count, 3);
            fuzzyCompare(tested.items.get(0).item.color, "red", 0);
            fuzzyCompare(tested.items.get(1).item.color, "red", 0);
            fuzzyCompare(tested.items.get(2).item.color, "green", 0);
        }

        function test_remove() {
            tested.remove(1);
            compare(tested.count, 3);
            fuzzyCompare(tested.items.get(0).item.color, "red", 0);
            fuzzyCompare(tested.items.get(1).item.color, "green", 0);
            fuzzyCompare(tested.items.get(2).item.color, "blue", 0);
        }

        function test_select() {
            let but = tested.items.get(0).item.lebutton;
            tested.select(but, "blue");
            compare(tested.count, 4);
            tryCompare(tested.items.get(0), "loaded", true);
            fuzzyCompare(tested.items.get(0).item.color, "blue", 0);
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
