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
  //  cursorPosition: data.curseur
  onSectionIdChanged: {
    data = ddb.loadSection(sectionId)
    //    updating = true
    text = data.content
    cursorPosition = data.curseur
    //    print(text)
  }

  background: Rectangle {
    anchors.fill: parent
    color: "white"
  }
  //  font.wordSpacing: 0
  font.family: "Courier"

  function sleepFor(sleepDuration) {
    var now = new Date().getTime();
    while (new Date().getTime() < now + sleepDuration) {
      /* do nothing */
    }
  }

  Keys.onPressed: {
    //    var okKeys = [Qt.Key_Up, Qt.Key_Down, Qt.Key_Right,
    //      Qt.Key_Left, Qt.Key_Shift, Qt.Key_Del, Qt.Key_Backspace
    //    ]
    //    if (!okKeys.includes(event.key)) {
    var new_data = ddb.updateEquation(sectionId, text, cursorPosition, JSON.stringify(event))
    root.data = new_data
    root.text = new_data.content
    root.cursorPosition = new_data.curseur
    event.accepted = true
    //    return
    //    }
    //    print("pppppppppppas", event.text)
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