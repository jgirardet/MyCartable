import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/layouts"

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
