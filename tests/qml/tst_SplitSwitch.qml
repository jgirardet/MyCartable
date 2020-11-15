import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/layouts"

Item {
    id: item

    width: 400
    height: 400

    Component {
        //        }

        id: red

        Rectangle {
            property alias sw: sw

            color: "red"

            SplitSwitch {
                id: sw

                mainItem: sl
                anchors.centerIn: parent
            }

        }

    }

    Component {
        id: blue

        Rectangle {
            property alias sw: sw

            color: "blue"

            SplitSwitch {
                id: sw

                mainItem: sl
                anchors.centerIn: parent
            }

        }

    }

    Component {
        id: green

        Rectangle {
            property alias lebutton: lebutton
            property alias sw: sw

            color: "green"

            Column {
                anchors.fill: parent

                Button {
                    id: lebutton

                    text: "bla"
                }

                SplitSwitch {
                    id: sw

                    mainItem: sl
                }

            }

        }

    }

    SplitLayout {
        id: sl

        anchors.fill: parent
        layouts: {
            "red": {
                "splittype": "red",
                "splittext": "lered",
                "spliturl": "",
                "splitcomp": red,
                "splitindex": 0
            },
            "blue": {
                "splittype": "blue",
                "splittext": "leblue",
                "spliturl": "",
                "splitcomp": blue,
                "splitindex": 1
            },
            "green": {
                "splittype": "green",
                "splittext": "legreen",
                "spliturl": "",
                "splitcomp": green,
                "splitindex": 2
            }
        }
        initDataModel: ["green"]
    }

    CasTest {
        function initPre() {
            sl.items.clear();
        }

        function test_init() {
            compare(sl.count, 0);
        }

        function test_model() {
            sl.append("red");
            let zero = sl.get(0);
            tryCompare(zero, "loaded", true);
            let m = zero.item.sw;
            compare(m.model, sl.layoutsAsArray);
        }

        function test_text_on_load() {
            sl.append("red");
            sl.append("blue");
            sl.append("green");
            tryCompare(sl.get(2), "loaded", true);
            compare(sl.get(0).item.sw.currentText, "lered");
            compare(sl.get(1).item.sw.currentText, "leblue");
            compare(sl.get(2).item.sw.currentText, "legreen");
        }

        function test_get_index_on_load() {
            sl.append("red");
            sl.append("blue");
            sl.append("green");
            tryCompare(sl.get(2), "loaded", true);
            compare(sl.get(2).item.sw.currentIndex, 2);
        }

        function test_change_value() {
            sl.append("red");
            tryCompare(sl.get(0), "loaded", true);
            compare(sl.get(0).item.sw.currentText, "lered");
            fuzzyCompare(sl.get(0).item.color, "red", 0);
            mouseClick(sl.get(0).item.sw);
            keyClick(Qt.Key_Down);
            keyClick(Qt.Key_Return);
            tryCompare(sl.get(0), "loaded", true);
            tryCompare(sl.get(0).item.sw, "currentIndex", 1);
            compare(sl.get(0).item.sw.currentText, "leblue");
            fuzzyCompare(sl.get(0).item.color, "blue", 0);
        }

        name: "SplitSwitch"
        testedNom: "qrc:/qml/menu/SplitSwitch.qml"
        autocreate: false
    }

}
