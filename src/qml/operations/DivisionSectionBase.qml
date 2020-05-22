import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.14

RowLayout {
  id: root
  /* beautify preserve:start */
  property int sectionId
  property var sectionItem
  property var model
  /* beautify preserve:end */
  BaseOperation {
    id: corps
    objectName: "corps"
    cellWidth: 16
    cellHeight: 30
    sectionId: root.sectionId
    model: root.model
    sectionItem: root.sectionItem
    delegate: DivisionDelegate {
      id: divdelegate
      quotient: quotientField
    }
    Component.onCompleted: {
      model = root.model
    }

  }
  Rectangle {
    height: corps.height
    Layout.preferredWidth: 5
    color: "black"
  }
  ColumnLayout {
    height: corps.height
    //    width: 200
    Layout.preferredWidth: 200
    Label {
      id: diviseur
      Layout.preferredHeight: corps.cellHeight
      Layout.preferredWidth: 200
      //      text: sectionId ?  corps.model.diviseur : undefined
      background: Rectangle {
        color: "white"
      }
      Binding on text {
        when: root.model.sectionId
        value: corps.model.diviseur
      }
    }
    Rectangle {
      Layout.preferredHeight: 5
      Layout.preferredWidth: 200
      color: "black"
    }
    TextField {
      id: quotientField
      Layout.preferredWidth: 200
      objectName: "quotientField"
      onTextEdited: {}
      Binding on text {
        when: root.model.sectionId
        value: corps.model.quotient
      }

      Keys.onReturnPressed: {
        corps.model.getPosByQuotient()
      }
      validator: RegularExpressionValidator {
        regularExpression: /^(\d+,?(\d+)?)?$/
      }
    }
    Item {
      Layout.fillHeight: true
    }
  }
}