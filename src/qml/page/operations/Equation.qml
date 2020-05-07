import QtQuick 2.14
import QtQuick.Controls 2.14

TextArea {
  id: root
  property int sectionId
  width: base.width - 20
  height: contentHeight + 30
  font.pointSize: 12
  /* beautify preserve:start */
  property var data: {"content":"\n\n"}
  property var base
  property var updating: false
  /* beautify preserve:end */
  //  text: data.content
  cursorPosition: data.curseur
  onSectionIdChanged: {
    data = ddb.loadSection(sectionId)
    updating = true
    text = data.content
    cursorPosition = data.curseur
  }

  background: Rectangle {
    anchors.fill: parent
    color: "white"
  }

  Keys.onPressed: {
    print(event)
    ddb.updateEquation(sectionId, text, cursorPosition, event.key, event.modifiers)

    //    if (!updating) {
    //      updating = true
    //      data = ddb.updateEquation(sectionId, text, cursorPosition)
    //      print("textlength change", JSON.stringify(data))
    //      text = data.content
    //      print("cursor", data.curseur)
    //      cursorPosition = data.curseur
    //
    //    } else {
    //      updating = false
    //    }
    //    print(print(JSON.stringify(res)))
    //    if (res.code == 200) {
    //      root.text = text.data
    //    }
    //    event.accepted = true
  }
}