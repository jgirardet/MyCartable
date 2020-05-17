import QtQuick 2.14
import QtQuick.Controls 2.14

BaseMenu {
  id: menu
  MenuItem {
    Column {
      ToolButton {
        text: qsTr("90°")
        onClicked: {
          print(target)
          var res = ddb.pivoterImage(menu.target.sectionId, 90)
          if ('res') {
            print(target.image.source)
            target.reloadImage()
          }

          menu.ferme()
          //            var content = ddb.loadSection(sectionId)
          //            var path = content.path.toString()
          //            img.source = path.startsWith("file:///") || path.startsWith("qrc:") ? content.path : "file:///" + path

        }
        ToolTip.text: "Pivoter l'image de 90°"
      }
    }
  }
}