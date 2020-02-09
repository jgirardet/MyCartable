import QtQuick 2.14
import QtQuick.Controls 2.14
import DocumentEditor 1.0

TextArea {
  id: area
  property QtObject base
  property int sectionId

  selectByMouse: true
  wrapMode: TextEdit.Wrap
  width: base.width
//  textFormat: TextEdit.RichText

  MouseArea {
    anchors.fill: area
    acceptedButtons: Qt.RightButton

    onPressed: {

      if (pressedButtons == Qt.RightButton) {
        var d = area.selectionStart
        var f = area.selectionEnd
        menu.popup()
        cursorPosition = d
        moveCursorSelection(f, TextEdit.SelectCharacters)

      }

    }
  }

  Keys.onPressed: {
        if (event.key == Qt.Key_Return) {
            var accept = doc.inspect()
            event.accepted = accept
        }
    }
//
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
  }

  MenuFlottant {
    id: menu
    editor: doc
  }
}