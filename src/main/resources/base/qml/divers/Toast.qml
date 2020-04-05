import QtQuick 2.14
import QtQuick.Controls 2.14

Popup {
  id: popup
  property string msg
  property color bgcolor: "yellow"
  property color txtcolor: "red"


  background: Rectangle {
    implicitWidth: 200
    implicitHeight: 60
    color: popup.bgcolor
  }
//  y: (rootWindow.height - 60)
  modal: true
  focus: true
  closePolicy: Popup.CloseOnPressOutside
  Text {
    id: message
    anchors.centerIn: parent
    font.pointSize: 12
    color: popup.txtcolor
    text: popup.msg
    onTextChanged: {print(text)}
  }
  onOpened: popupClose.start()
  Timer {
    id: popupClose
    interval: 2000
    onTriggered: popup.close()
  }
}

// Popup will be closed automatically in 2 seconds after its opened