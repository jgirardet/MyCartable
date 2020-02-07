import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.12
import QtQuick.Controls.Styles 1.4

Menu {
  id: menu
  property QtObject document
  signal styleChange(var data)




MenuItem {
  RowLayout {
    anchors.fill: parent
    spacing: 0
    Button {
      id: but
      background: Rectangle {anchors.fill: parents; color: "red"}
      highlighted: but.pressed
      Layout.fillHeight: true
//      Layout.fillWidth: true
//      color: "red"
//      MouseArea{
//      anchors.fill: parent
      action: rouge
      text: qsTr("rouge")
      Action {
          id: rouge
          onTriggered: {
          print('trig')
          document.setStyle({"type": "color", "value":"red"})
          }
      }
      }
    }
   }

//      }
//    Button {
//      Layout.fillWidth: true
//      color: "red"
//      MouseArea{
//      anchors.fill: parent
//      onClicked: rouge.trigger()
//      text: qsTr("bleu")
//      Action {
//        Layout.fillHeight: true
//        Layout.fillWidth: true
//          id: rouge
//          onTriggered: {
//          print('trig')
//          document.setStyle({"type": "color", "value":"red"})
//          }
//      }
//      Action {
//              Layout.fillWidth: true
//        Layout.fillHeight: true
//          id: bleu
//          onTriggered: {
//          print('trig')
//          document.setStyle({"type": "color", "value":"bleu"})
//          }
//      }
//      }
//      }
//    Rectangle {Layout.fillHeight: true;Layout.fillWidth: true;color: "blue"}
//    Rectangle {Layout.fillHeight: true;Layout.fillWidth: true;color: "green"}
//    Rectangle {Layout.fillHeight: true;Layout.fillWidth: true;color: "black"}
//    Rectangle {Layout.fillHeight : true; width: height; color: "blue"}
//      Action {
//      text: qsTr("rouge")
//      onTriggered: document.setStyle({"type": "color", "value":"red"})
//    }

//  }


//  Action {
//    text: qsTr("Tool Bar")
//  }
//  Action {
//    text: qsTr("Side Bar")

//
//  MenuSeparator {
//    contentItem: Rectangle {
//      implicitWidth: 200
//      implicitHeight: 1
//      color: "#21be2b"
//    }
//  }

  Action {
    text: qsTr("Status Bar");checkable: true;checked: true
  }

}