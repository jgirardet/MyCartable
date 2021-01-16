import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.12

Button {
    id: root

    property alias shortcut: action.shortcut
    property color color
    property var menu
    property var style
    property var attrs: Object()

    Layout.fillHeight: true
    Layout.fillWidth: true
    highlighted: pressed
    action: action

    Action {
        id: action

        onTriggered: {
            menu.target.setStyleFromMenu({
                "style": style,
                "attrs": attrs
            });
            menu.close();
        }
    }

    background: Rectangle {
        id: back

        color: root.color
        anchors.fill: parent
    }

}
