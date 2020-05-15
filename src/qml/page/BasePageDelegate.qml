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
    objectName: "dragitem"
    Loader {
      id: loader
      objectName: "loader"
    }

    width: loader.width
    height: loader.height
    color: "transparent"
    anchors {
      verticalCenter: parent.verticalCenter
    }
    Drag.active: dragArea.held
    Drag.source: dragArea
    Drag.hotSpot.x: width / 2
    Drag.hotSpot.y: height / 2
    states: State {
      when: dragArea.held
      PropertyChanges {
        target: dragitem
        color: "steelblue"
        opacity: 0.6

      }

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
  }

  MouseArea {
    id: dragArea
    anchors.fill: parent
    property bool held: false
    height: loader.height

    drag.target: held ? dragitem : undefined
    drag.axis: Drag.YAxis
    acceptedButtons: Qt.LeftButton | Qt.MiddleButton

    onPressed: {
      if ((mouse.button == Qt.LeftButton) && (mouse.modifiers & Qt.ShiftModifier)) {
        held = true
        mouse.accepted = true

      } else if ((mouse.button == Qt.MiddleButton) && (mouse.modifiers & Qt.ShiftModifier)) {
        var coord = mapToItem(listview, mouse.x, mouse.y)
        listview.removeDialog.ouvre(index, coord)

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
      fill: root
      margins: 10
    }
    onEntered: {
      listview.model.move(drag.source.parent.modelIndex, index)
    }
  }
  MouseArea {
    height: listview.spacing
    width: root.width
    //    color: "green"
    anchors.top: root.bottom
    acceptedButtons: Qt.RightButton
    onClicked: {
      if ((mouse.button == Qt.RightButton) && (mouse.modifiers & Qt.ShiftModifier)) {
        var coord = mapToItem(listview, mouse.x, mouse.y)
        listview.addDialog.ouvre(index, coord)
      }
    }
  }
  Component.onCompleted: {
    loader.setSource(`qrc:/qml/sections/${page.classtype}.qml`, {
      "sectionId": sectionId,
      "sectionItem": root,
    })
  }

}