import QtQuick 2.14
import QtQuick.Controls 2.14
import DocumentEditor 1.0

TextArea {
  id: area
  property QtObject base
  property int sectionId
  wrapMode: TextEdit.Wrap
  width: base.width

  property DocumentEditor doc: DocumentEditor {
    id: doc
    document: area
    position: cursorPosition
    Binding on sectionId {
      when: doc.documentChanged
      value: area.sectionId
    }
    }


}
