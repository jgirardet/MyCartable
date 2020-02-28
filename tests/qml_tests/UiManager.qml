import QtQuick 2.14
import "qrc:/qml/menu"

Item {
      /* beautify preserve:start */
      property var menuTarget
      property var menuFlottantText: _menuFlottantText
      /* beautify preserve:end */

      MenuFlottantText {
        id: _menuFlottantText
      }
    }