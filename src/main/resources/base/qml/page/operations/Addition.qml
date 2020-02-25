import QtQuick 2.14
import QtQuick.Controls 2.14



GridView {
        id: root
        property int position
        property int sectionId
//        currentIndex: model.cursor
        /* beautify preserve:start */
        property var base
        /* beautify preserve:end */
//        anchors.fill: parent
        width: cellWidth *model.columns
        height: cellHeight * model.rows
        cellWidth: 50
        cellHeight: 50
//        focus: true
//        onFocusChanged: {delegateRectangle.focus=focus}
//        onCurrentIndexChanged: focus=true
        delegate: Rectangle {
            id: delegateRectangle
            height: root.cellHeight
            width: root.cellWidth
            color: "white"
            border.width: 0.5
            TextInput {
              id: input
//              focus: delegateRectangle.focus
//              focus: true
//              onFocusChanged: root.model.cursor=index
              anchors.fill: parent
              text: display
              horizontalAlignment: TextInput.AlignHCenter
              verticalAlignment: TextInput.AlignVCenter
              readOnly: root.model.readOnly(index)
              validator: IntValidator{bottom: 0; top: 9;}
              onTextEdited:{
              root.model.autoMoveNext(index)
              root.forceActiveFocus()
              }
//
              }
//
          }

         Binding on currentIndex {
          when: model.cursorChanged
          value: model.cursor
    }
    }