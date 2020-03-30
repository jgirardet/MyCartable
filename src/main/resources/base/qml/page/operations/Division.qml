import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.14

RowLayout {
  id: root
  property  alias model: corps.model
  property alias sectionId: corps.sectionId
  property alias position: corps.position
  BaseOperation {
    id: corps
    objectName: "corps"
    cellWidth: 30
    cellHeight: 30
    delegate: DivisionDelegate {
      model: corps.model
      quotient: quotientField
    }
  }
  Rectangle {
    height: corps.height
    width: 5
    color: "black"
//    anchors.margins: 0
  }
  ColumnLayout {
    height: corps.height
    width: 200
    Label {
      id: diviseur
      Layout.preferredHeight: corps.cellHeight
      Layout.preferredWidth: 100
      text: corps.model.diviseur
      background: Rectangle {color: "white"}
    }
    Rectangle {
      Layout.preferredHeight: 5
      Layout.preferredWidth: 200
      color: "black"
    }
    TextField {
      id: quotientField
      objectName: "quotientField"
      text: corps.model.quotient
      onTextEdited : {corps.model.quotient=text}
      onEditingFinished: {corps.forceActiveFocus()}
      validator: RegularExpressionValidator {
         regularExpression: /^\d{1},?$/
        }
    }
    Item {
        Layout.fillHeight: true
    }
  }
}