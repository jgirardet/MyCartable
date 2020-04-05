import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Window 2.14
import QtQuick.Layouts 1.14
import "matiere"
import "recents"
import "page"
import "divers"

ApplicationWindow {
  id: root
  width: 800
  height: 600
  visible: true
  header: MainMenuBar {
    id: mainMenuBar
  }
  onClosing: {
    baseItem.destroy() // elmine presque tous les messages d'erreur
  }
  Item {
    id: baseItem
    objectName: "baseItem"
    height: root.height - mainMenuBar.height
    width: root.width
    RowLayout {
      anchors.fill: parent
      RecentsRectangle {
        id: _recentsRectangle
        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.preferredWidth: ddb.getLayoutSizes("preferredSideWidth")
        Layout.maximumWidth: ddb.getLayoutSizes("maximumSideWidth")
        Layout.minimumWidth: ddb.getLayoutSizes("minimumSideWidth")
      }
      PageRectangle {
        id: _pageRectangle
        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.preferredWidth: ddb.getLayoutSizes("preferredCentralWidth")
        Layout.minimumWidth: ddb.getLayoutSizes("minimumCentralWidth")
      }
      MatiereRectangle {
        id: _matiereRectangle
        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.preferredWidth: ddb.getLayoutSizes("preferredSideWidth")
        Layout.maximumWidth: ddb.getLayoutSizes("maximumSideWidth")
        Layout.minimumWidth: ddb.getLayoutSizes("minimumSideWidth")
      }
    }
  }
}