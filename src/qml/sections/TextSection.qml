import QtQuick 2.14
import QtQuick.Controls 2.14
import DocumentEditor 1.0
import "qrc:/qml/menu"

// TODO: interlignes doubles

TextArea {
  id: area
  /* beautify preserve:start */
  property int sectionId
  property var sectionItem
  /* beautify preserve:end */
  //  property var listview

  selectByMouse: true
  wrapMode: TextEdit.Wrap
  width: sectionId ? sectionItem.width : undefined
  //  focus: true
  //  focus: parent.ListView.isCurrentItem

  onFocusChanged: {

    if (focus) {
      uiManager.menuTarget = doc
    }
  }

  MouseArea {
    anchors.fill: area
    acceptedButtons: Qt.LeftButton | Qt.RightButton

    onPressed: {
      if (pressedButtons == Qt.LeftButton) {
        uiManager.menuTarget = doc
        mouse.accepted = false
      } else if (pressedButtons == Qt.RightButton) {
        menuStylePopup(area.selectionStart, area.selectionEnd)
      }

    }
  }
  Keys.onPressed: {
    if (event.key == Qt.Key_Return) {
      event.accepted = doc.paragraphAutoFormat()
    }
  }

  function menuStylePopup(start, end) {
    uiManager.menuFlottantText.ouvre(doc)
    cursorPosition = start
    moveCursorSelection(end, TextEdit.SelectCharacters)
  }

  property DocumentEditor doc: DocumentEditor {
    id: doc
    document: area
    Binding on sectionId {
      when: doc.documentChanged
      value: area.sectionId
    }
    Binding on selectionStart {
      when: doc.documentChanged
      value: area.selectionStart
    }
    Binding on selectionEnd {
      when: doc.documentChanged
      value: area.selectionEnd
    }

    onSelectionStartChanged: function() {
      area.cursorPosition = selectionStart
    }
    onSelectionCleared: area.deselect()
    //    onDocumentContentChanged: {area.text}

  }
  background: Rectangle {
    anchors.fill: parent
    color: "white"
  }
}