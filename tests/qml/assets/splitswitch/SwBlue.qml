import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/layouts"

Rectangle {
    property alias sw: sw

    color: "blue"

    SplitSwitch {
        id: sw

        mainItem: sl
        anchors.centerIn: parent
    }

}
