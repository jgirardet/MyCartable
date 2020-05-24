import QtQuick 2.14
import QtQuick.Controls 2.14

TextEdit {
  id: root
  /* beautify preserve:start */
  property int sectionId
  property var sectionItem
  property bool doNotUpdate: false
  /* beautify preserve:end */
  font.pointSize: 20 // necéssaire pour que les taille html soient corrent == taille de p
  height: contentHeight + 30
  width: sectionItem.width
  textFormat: TextEdit.RichText
  leftPadding: 10
  rightPadding: 10
  selectByMouse: true
  wrapMode: TextEdit.Wrap

  Keys.onPressed: {
    var res = ddb.updateTextSectionOnKey(sectionId, text, cursorPosition, selectionStart, selectionEnd, JSON.stringify(event))
    event.accepted = res["eventAccepted"]
    if (event.accepted == false) {
      return
    } else {
      doNotUpdate = true
      text = res["text"]
      cursorPosition = res["cursorPosition"]
      //      print(text)
    }
  }
  onSectionIdChanged: {
    var res = ddb.loadTextSection(sectionId)
    doNotUpdate = true
    text = res["text"]
    cursorPosition = res["cursorPosition"]
    //    print(text)
  }
  onTextChanged: {
    if (doNotUpdate) {
      doNotUpdate = false
      return
    } else {
      var res = ddb.updateTextSectionOnChange(sectionId, text, cursorPosition, selectionStart, selectionEnd)
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

}