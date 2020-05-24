import QtQuick 2.14
import QtQuick.Controls 2.14

TextEdit {
  id: root
  /* beautify preserve:start */
  property int sectionId
  property var sectionItem
  property bool doNotUpdate: false
  /* beautify preserve:end */
  width: sectionItem.width
  height: contentHeight + 30
  font.pointSize: 20 // necéssaire pour que les taille html soient corrent == taille de p
  //  font.pointSize: 20 // necéssaire pour que les taille html soient corrent == taille de p
  //  font.weight: Font.Thin
  textFormat: TextEdit.RichText
  selectByMouse: true
  wrapMode: TextEdit.Wrap
  //  text: "nlbnmj"
  onTextChanged: {
    if (doNotUpdate) {
      doNotUpdate = false
      return
    } else {
      var res = ddb.updateTextSectionOnChange(sectionId, text, cursorPosition, selectionStart, selectionEnd)

      //      event.accepted = res["eventAccepted"]
      print(text)
      if (res["eventAccepted"]) {
        // ici event Accepted veut dire : on ne remet pas à jour le text
        return
      } else {
        doNotUpdate = true
        text = res["text"]
        cursorPosition = res["cursorPosition"]

      }
    }
  }
  //  Keys.onPressed: {
  //    var res = ddb.updateTextSectionOnKey(sectionId, text, cursorPosition, selectionStart, selectionEnd, JSON.stringify(event))
  //    event.accepted = res["eventAccepted"]
  //    print(text)
  //    if (event.accepted == false) {
  //      return
  //    } else {
  //      doNotUpdate = true
  //      text = res["text"]
  //      cursorPosition = res["cursorPosition"]
  //    }
  //  }

  onSectionIdChanged: {
    var res = ddb.loadTextSection(sectionId)
    doNotUpdate = true
    text = res["text"]
    cursorPosition = res["cursorPosition"]
    print(text)
  }

}