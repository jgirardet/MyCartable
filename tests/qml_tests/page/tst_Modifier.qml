import QtQuick 2.14
import QtTest 1.14
Item {
  width: 200
  height: 200
  id: item
  MouseArea {
    anchors.fill: parent
    onClicked: {
      print("click ", mouse.modifiers)
    }
    onPositionChanged: {
      print('drag : ', mouse.modifiers)
    }
  }

  TestCase {
    name: "my test"
    when: windowShown

    function test_click() {
      mouseClick(item, item.width / 2,item.height / 2, Qt.LeftButton, Qt.ControlModifier,  -1)
      mouseDrag(item, item.width / 2,  item.height / 2,1, 1, Qt.LeftButton, Qt.ControlModifier,  -1)
    }
  }
}