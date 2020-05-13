import QtQuick 2.14
import QtQuick.Controls 2.14

Item {
  id: root
  /* beautify preserve:start */
  property var listview: ListView.view
  property int sectionId: page.id
    property int modelIndex: typeof model !== "undefined" ? model.index : undefined
  /* beautify preserve:end */
  width: listview.width
  height: loader.height
  Rectangle {
    id: dragitem
    //    anchors.fill: parent
    width: listview.width
    height: loader.height
    color: dragArea.held ? "lightsteelblue" : "transparent"
    anchors {
      verticalCenter: parent.verticalCenter
    }
    Drag.active: dragArea.held
    Drag.source: dragArea
    Drag.hotSpot.x: width / 2
    Drag.hotSpot.y: height / 2
    states: State {
      when: dragArea.held

      ParentChange {
        target: dragitem;parent: listview.contentItem
      }
      AnchorChanges {
        target: dragitem
        anchors {
          horizontalCenter: undefined;verticalCenter: undefined
        }
      }
    }

    Loader {
      id: loader

    }
  }

  MouseArea {
    id: dragArea
    anchors.fill: parent
    property bool held: false
    height: loader.height

    drag.target: held ? dragitem : undefined
    drag.axis: Drag.YAxis

    onPressed: {
      if ((mouse.button == Qt.LeftButton) && (mouse.modifiers & Qt.ControlModifier)) {
        held = true
        mouse.accepted = true
      } else {
        mouse.accepted = false
      }
    }
    onReleased: {
      held = false
    }
  }
  DropArea {
    id: droparea
    anchors {
      fill: root;
    }

    onEntered: {
      listview.model.move(drag.source.parent.modelIndex, index)
    }
  }

  Component.onCompleted: {
    loader.setSource(`qrc:/qml/sections/${page.classtype}.qml`, {
      "sectionId": sectionId,
      "sectionItem": root,
    })
  }
}