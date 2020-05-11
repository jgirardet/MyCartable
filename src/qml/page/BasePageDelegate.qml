import QtQuick 2.14
import QtQuick.Controls 2.14

Item {
  id: root
  /* beautify preserve:start */
  property var listview: ListView.view
  property int sectionId: page.id
  property int position: page.position
  width: listview.width
  height: loader.height
  /* beautify preserve:end */

  Loader {
    id: loader
  }

  MouseArea {
    anchors.fill: root
    onPressed: {
      //      listview.currentIndex = position
      //      loader.item.focus == true
      print(listview.width)
      mouse.accepted = false
    }
  }
  Component.onCompleted: {
    loader.setSource(`qrc:/qml/sections/${page.classtype}.qml`, {
      "sectionId": sectionId,
      "sectionItem": root,
    })
  }
}
//  Component.onCompleted: {
//    content.z = 1
//  }
//  Rectangle {
//    anchors.fill: parent
//    color: "yellow"
//  }

//  drag.target: held ? content : undefined
//  drag.axis: Drag.YAxis

//  onPressed: {
//    print("éblabl")
//    if ((mouse.button == Qt.LeftButton) && (mouse.modifiers & Qt.ControltModifier)) {
//      print("avant accepte")
//      event.accepted = true
//      print("apres accept")
//      //        doSomething();
//    }
//  }
//  onPressAndHold: {
//    held = true
//    print(held)
//  }
//  onReleased: {
//    held = false
//
//    print(held)
//
//  }
//}