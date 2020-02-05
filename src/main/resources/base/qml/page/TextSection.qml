import QtQuick 2.14
import QtQuick.Controls 2.14
import TextSectionClass 1.0

//Item {
//property int sectionId
//height: parent.width
//


TextArea {
  id: area
  property QtObject base
  property alias sectionId: document.sectionId
  width: base.width
  wrapMode: TextEdit.Wrap
//  onFocusChanged: {
//    if (focus) {
//    ddb.setDocument(area)

  property TextSectionR doc: TextSectionR {
      id: document
      document: area
  }
}
//  Component.onCompleted: {
//    //ddb.document = textDocument
//  }
//TextSectionR {
//
//}
//}

