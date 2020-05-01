import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.14

import "qrc:/qml/divers"

Rectangle {
  id: base
  /* beautify preserve:start */
  property var model
  /* beautify preserve:end */
  color: "transparent"
  height: lv.height + header.height + 10

  Column {
    //    anchors.fill: parent
    spacing: 5

    Rectangle {
      id: header
      objectName: "header"
      height: 30
      color: ddb.currentMatiereItem.bgColor
      radius: 10
      width: base.width
      property MouseArea mousearea: headerMouseArea
      property Label label: headerLabel

      Label {
        id: headerLabel
        text: base.model.nom
        //        text: "modelData.nom"
        anchors.centerIn: parent
      }

      MouseArea {
        id: headerMouseArea
        acceptedButtons: Qt.RightButton
        anchors.fill: parent
        onPressed: {
          if (mouse.buttons == Qt.RightButton) {
            ddb.newPage(model.id)
          }
        }
      }
    }

    ListView {
      id: lv
      objectName: "lv"
      //    anchors.fill: parent
      property int commonHeight: 30
      model: base.model.pages
      spacing: 3
      width: base.width
      height: lv.contentItem.childrenRect.height
      delegate: PageButton {
        id: but
        width: ListView.view.width
        height: lv.commonHeight
        model: modelData
        borderDefaultWidth: 0
        Component.onCompleted: {
          background.color = "#cdd0d3"
        }
      }
    }
  }
}