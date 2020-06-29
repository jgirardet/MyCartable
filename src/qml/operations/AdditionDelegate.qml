import QtQuick 2.14
import QtQuick.Controls 2.14
import "qrc:/qml/divers"

Rectangle {
    id: root

    property alias model: input.model
    property alias textinput: input
    property GridView grid: GridView.view

    height: grid.cellHeight
    width: grid.cellWidth
    color: "white"

    TextInputDelegate {
        id: input

        bottomPadding: model.isRetenueLine(index) ? 0 : 5
        topPadding: model.isMiddleLine(index) ? 0 : 5
        anchors.fill: parent
        color: model.isRetenueLine(index) ? "red" : "black"
        horizontalAlignment: TextInput.AlignHCenter
        verticalAlignment: model.isResultLine(index) ? TextInput.AlignVCenter : model.isRetenueLine(index) ? TextInput.AlignBottom : TextInput.AlignTop
    }

}
