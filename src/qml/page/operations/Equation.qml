import QtQuick 2.14
import QtQuick.Controls 2.14

TextArea {
  id: root
  property sectionId

  Binding on text {
    when: sectionId
    target: root
    property: "text"
    value: ddb.pullEquation(sectionId)
  }

  Keys.pressed: {

    res = ddb.sendEquation()
    if (res.code == 200) {
      root.text = text.data
    }
    event.accepted = True
  }
}