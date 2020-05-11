import QtQuick 2.14
import QtQuick.Controls 2.14
import "../../divers"

Rectangle {
  id: root
  property alias model: input.model
  property alias textinput: input
  property TextInput quotient
  property GridView grid: GridView.view
  height: grid.cellHeight
  width: grid.cellWidth
  focus: !model.isRetenue(index)
  color: "white"

  signal jumpToQuotient()

  TextInputDelegate {
    id: input

    anchors.fill: parent
    color: model.isRetenue(index) ? "red" : "black"
    horizontalAlignment: model.isRetenueGauche(index) ? TextInput.AlignRight : model.isRetenueDroite(index) ? TextInput.AlignLeft : TextInput.AlignHCenter
    verticalAlignment: TextInput.AlignVCenter
    font.pointSize: root.grid.cellWidth - 6
    background: BorderRectangle {
      //      width: input.contentWidth
      color: input.focus ? "yellow" : root.color
      border.width: 0
      borderColor: model.isMembreLine(index + model.columns) ? "black" : input.parent.color
      borderTop: -2
    }
    padding: 0
    leftInset: 0
    rightInset: 0
    readOnly: !model.isEditable(index)
    activeFocusOnPress: model.isEditable(index)
    //    readOnly: !model.isDividendeLine(index)

    //    readOnly: model.isRetenue(index)

    //    onPressed: {
    //      if (model.isRetenue(index)) {
    //        input.focus = false
    //        print('block', event)
    //        event.accepted = false // block la souris pour retenues
    //      }
    //    }

    function moreKeys(event) {
      if (event.key == Qt.Key_Return) {
        //        jumpToQuotient.emit()
        root.quotient.forceActiveFocus()
        event.accepted = true

      } else if (event.key == Qt.Key_Plus) {
        model.goToAbaisseLine()
        event.accepted = true
      } else if (event.key == Qt.Key_Minus) {
        model.goToResultLine()
        event.accepted = true

      } else if (event.key == Qt.Key_Asterisk) {
        model.addRetenues()
        event.accepted = true

      }

    }

  }

}