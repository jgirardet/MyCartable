import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.14
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
      //    headerPositioning: ListView.OverlayHeader
      delegate: Button {
        id: but
        width: ListView.view.width
        height: lv.commonHeight
        highlighted: hovered
        contentItem: Label {
          text: modelData.titre
          color: ddb.currentMatiereItem.fgColor
          verticalAlignment: Text.AlignVCenter
        }
        onClicked: {
          ddb.currentPage = modelData.id

        }
        background: Rectangle {
          anchors.fill: parent
          radius: 10
          //        color:  ddb.currentMatiereItem.bgColor
          color: "#cdd0d3"
          border.width: highlighted ? 3 : 1
          //          border.color: modelData ? Qt.darker(modelData.bgColor, 3) : "white"
        }
      }
    }
  }
}