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


  MouseArea {
    anchors.fill: area
    acceptedButtons: Qt.RightButton

  onPressed: {

    if (pressedButtons == Qt.RightButton) {
      var d = area.selectionStart
      var f = area.selectionEnd
      menu.popup()
      print("apres popup")
      cursorPosition = d
      print('entre position et movecuroser')
      moveCursorSelection(f, TextEdit.SelectCharacters)
      print(cursorPosition, selectionStart, selectionEnd)


    }

  }
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
  }

  MenuFlottant {
    id: menu
    document: doc
  }
}