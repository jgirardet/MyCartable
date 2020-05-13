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
    anchors {
      //      horizontalCenter: parent.horizontalCenter
      verticalCenter: parent.verticalCenter
    }
    Drag.active: dragArea.held
    Drag.source: dragArea
    Drag.hotSpot.x: width / 2
    Drag.hotSpot.y: height / 2
    states: State {
      when: dragArea.held

      ParentChange {
        target: loader;parent: listview.contentItem
      }
      AnchorChanges {
        target: loader
        anchors {
          horizontalCenter: undefined;verticalCenter: undefined
        }
      }
    }
  }

  //
  MouseArea {
    id: dragArea
    anchors.fill: parent
    property bool held: false
    //
    //    anchors {
    //      left: parent.left;right: parent.right
    //    }
    height: loader.height

    drag.target: held ? loader : undefined
    drag.axis: Drag.YAxis

    onPressed: {
      if ((mouse.button == Qt.LeftButton) && (mouse.modifiers & Qt.ControlModifier)) {
        held = true
        mouse.accepted = true
      } else {
        mouse.accepted = false
      }
    }
    //    onPressAndHold: held = true
    onReleased: held = false
    //    }
    //    Rectangle {
    //      id: content
    //![0]
    //      anchors {
    //        horizontalCenter: parent.horizontalCenter
    //        verticalCenter: parent.verticalCenter
    //      }
    //      width: dragArea.width;height: dragArea.height
    //
    //      border.width: 1
    //      border.color: "lightsteelblue"
    //
    //      color: dragArea.held ? "lightsteelblue" : "white"
    //      Behavior on color {
    //        ColorAnimation {
    //          duration: 100
    //        }
    //      }

    //      radius: 2
    //![1]
    //      Drag.active: dragArea.held
    //      Drag.source: dragArea
    //      Drag.hotSpot.x: width / 2
    //      Drag.hotSpot.y: height / 2
    //      //![1]
    //      states: State {
    //        when: dragArea.held
    //
    //        ParentChange {
    //          target: content;parent: root
    //        }
    //        AnchorChanges {
    //          target: content
    //          anchors {
    //            horizontalCenter: undefined;verticalCenter: undefined
    //          }
    //        }
    //      }

    //      Column {
    //        id: column
    //        anchors {
    //          fill: parent;margins: 2
    //        }
    //
    //        Text {
    //          text: 'Name: ' + name
    //        }
    //        Text {
    //          text: 'Type: ' + type
    //        }
    //        Text {
    //          text: 'Age: ' + age
    //        }
    //        Text {
    //          text: 'Size: ' + size
    //        }
    //      }
    //![2]
  }
  //![3]
  DropArea {
    anchors {
      fill: parent;margins: 10
    }

    onEntered: {
      print("drop areada", drag.source.parent, root)
      print(root.listview.model.index(root.position, 0), root.position)
      //        visualModel.items.move(
      //          drag.source.DelegateModel.itemsIndex,
      //          dragArea.DelegateModel.itemsIndex)
    }
  }
  //![3]
  //}

  Component.onCompleted: {
    loader.setSource(`qrc:/qml/sections/${page.classtype}.qml`, {
      "sectionId": sectionId,
      "sectionItem": root,
    })
  }
}

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