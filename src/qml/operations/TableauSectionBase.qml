import QtQuick 2.14
import QtQuick.Controls 2.14

Column {
  id: root
  /* beautify preserve:start */
  property int sectionId
  property var sectionItem
  property alias model: repDeLigne.model
  /* beautify preserve:end */
  width: sectionItem.width
  Repeater {
    id: repDeLigne

    //    model: [
    //      ["1", "2", "3", "2", "3", "2"],
    //      ["1", "2", "3", "2", "3", "2"],
    //      ["1", "2", "3", "2", "3", "2"],
    //      ["1", "2", "3", "2", "3", "2"],
    //      ["1", "2", "3", "2", "3", "2"],
    //      ["1", "2", "3", "2", "3", "2"],
    //    ]
    delegate: Row {
      Component.onCompleted: print(JSON.stringify(display))
      id: rowRow
      property int row: index
      Repeater {
        //        property int row: index
        model: display
        delegate: TextArea {
          text: `[${rowRow.row}:${index}] = ${modelData.y}, ${modelData.x}`
        }
      }
    }
  }
}