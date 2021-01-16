import QtQuick 2.15
import QtQuick.Controls 2.15

Column {
    property alias source: imgchooser.source
    property alias text: rb.icon.name
    property alias checked: rb.checked
    property var groupe: rb.ButtonGroup.group

    RadioButton {
        id: rb

        ButtonGroup.group: groupe
        display: AbstractButton.IconOnly
    }

    Image {
        id: imgchooser

        width: rb.width
        fillMode: Image.PreserveAspectFit
    }

}
