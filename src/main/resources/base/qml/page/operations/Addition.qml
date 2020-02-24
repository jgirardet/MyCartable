import QtQuick 2.14
import QtQuick.Controls 2.14



GridView {
        id: root
        property int position
        property int sectionId
        /* beautify preserve:start */
        property var base
        /* beautify preserve:end */
//        anchors.fill: parent
        width: base.width/3
        height: 300
        cellWidth: 50  //width/model.rowCount()
        cellHeight: 50 //height / model.columnCount()
//        height: 50*rows
//        contentWidth: width
//        contentHeight: height
         flow: GridView.FlowTopToBottom
//        height: 300
//        columnSpacing: 0
//        rowSpacing: 0
        delegate: Rectangle {
            id: delegateRectangle
            height: root.cellHeight
            width: root.cellWidth
////            implicitWidth: root.width / root.columns
////            implicitHeight: root.height / root.rows
            color: "white"
            border.width: 0.5
            TextInput {
              id: input
              anchors.fill: parent
              text: display + '        ' +  count
//              horizontalAlignment: TextInput.AlignHCenter
//              verticalAlignment: TextInput.AlignVCenter
////              readOnly: (column == 0 || (row > 0 && row < root.rows-1))  ? true : false
//              validator: IntValidator{bottom: 0; top: 9;}
//
              }
//
          }
    }