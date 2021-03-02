import QtQuick 2.15
import QtQuick.Controls 2.15

ToolButton {
    required property Menu menu

    icon.color: "transparent"
    ToolTip.visible: hovered

      onClicked: menu.close()

}
