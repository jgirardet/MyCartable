import QtQuick 2.14
import QtQuick.Controls 2.14
import "../toolbuttons"

ListView {

  id: root
  spacing: 10
  clip: true
  focus: true
  /* beautify preserve:start */
  property var removeDialog: removeDialog
  property var addDialog: addDialog
  /* beautify preserve:end */
  boundsBehavior: Flickable.DragOverBounds
  //  displayMarginEnd: 50

  delegate: BasePageDelegate {}
  onCurrentIndexChanged: {
    if (model.lastPosition !== currentIndex) {
      model.lastPosition = currentIndex
    }
  }
  footer: Rectangle {
    width: root.width
    //    height: root.height / 2
    implicitHeight: root.height / 2
    color: "transparent"
  }
  footerPositioning: ListView.OverlayFooter

  function onItemAdded(modelIndex, row, col) {
    positionViewAtIndex(row, ListView.Contain)
    currentIndex = row
  }
  Component.onCompleted: {
    model.rowsInserted.connect(onItemAdded)
  }
  ScrollBar.vertical: ScrollBar {
    minimumSize: 0.2
  }
  Connections {
    target: model
    function onModelReset() {
      if (currentIndex != model.lastPosition) {
        currentIndex = model.lastPosition
      }
    }
  }

  // TRANSITIONS
  remove: Transition {
    ParallelAnimation {
      NumberAnimation {
        property: "opacity";to: 0;duration: 1000
      }
      NumberAnimation {
        property: "scale";to: 0;duration: 500
      }
    }
  }
  removeDisplaced: Transition {
    NumberAnimation {
      properties: "x,y";duration: 500
    }
  }

  //  populate: Transition {
  //    NumberAnimation {
  //      property: "scale";from: 0;to: 1.0;duration: 800
  //    }
  //    NumberAnimation {
  //      properties: "x,y";duration: 800;easing.type: Easing.OutBack
  //    }
  //  }

  add: Transition {
    NumberAnimation {
      property: "opacity";from: 0;to: 1.0;duration: 1000
    }
    NumberAnimation {
      property: "scale";from: 0;to: 1.0;duration: 400
    }
  }

  displaced: Transition {
    NumberAnimation {
      properties: "x,y";duration: 800;easing.type: Easing.OutBounce
    }
  }

  Dialog {
    id: removeDialog
    objectName: "removeDialog"
    title: "Supprimer cet élément ?"
    property int index
    standardButtons: Dialog.Ok | Dialog.Cancel
    enter: Transition {
      NumberAnimation {
        property: "scale";from: 0.0;to: 1.0
      }
    }
    function ouvre(itemIndex, coords) {
      index = itemIndex
      open()
      x = coords.x - width / 2
      y = coords.y - height / 2
    }
    onAccepted: root.model.removeSection(index)

  }
  Dialog {
    id: addDialog
    title: "Ajotuer un élément ?"
    property int index
    enter: Transition {
      NumberAnimation {
        property: "scale";from: 0.0;to: 1.0
      }
    }

    contentItem: Row {

      NewTextSectionButton {
        id: newtext
        targetIndex: typeof addDialog.index != "undefined" ? addDialog.index + 1 : 0
        target: addDialog
      }
      NewImageSectionButton {
        targetIndex: newtext.targetIndex
        target: newtext.target
      }
      NewEquationSectionButton {
        targetIndex: newtext.targetIndex
        target: newtext.target
      }
      NewOperationSectionButton {
        targetIndex: newtext.targetIndex
        target: newtext.target
      }
      NewTableauSectionButton {
        targetIndex: newtext.targetIndex
        target: newtext.target
      }
    }
    function ouvre(itemIndex, coords) {
      index = itemIndex
      print("ouvre")
      open()
      x = coords.x - width / 2
      y = coords.y - height / 2
    }
  }

}