import QtQuick 2.15
import QtQuick.Controls 2.15
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

        function moreKeys(event) {
            if (event.key == Qt.Key_Asterisk) {
                model.addRetenues(index);
                event.accepted = true;
            }
        }

        height: parent / 2
        leftPadding: model.isRetenueDroite(index) ? 0 : 5
        rightPadding: model.isRetenueGauche(index) ? 1 : 5
        color: model.isRetenueGauche(index) || model.isRetenueDroite(index) ? "red" : "black"
        horizontalAlignment: model.isRetenueDroite(index) ? TextInput.AlignLeft : model.isRetenueGauche(index) ? TextInput.AlignRight : TextInput.AlignHCenter
        verticalAlignment: TextInput.AlignVCenter
    }

}
