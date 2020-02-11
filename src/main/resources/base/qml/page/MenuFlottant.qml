import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.12

Menu {
  id: root
  property QtObject editor
  signal styleChange(var data)

  MenuItem {
    RowLayout {
      anchors.fill: parent
      spacing: 0
      ColorButton {
        type: "color"
        color: "red"
        shortcut: "Ctrl+r"
        menu: root
      }
      ColorButton {
        type: "color"
        color: "blue"
        shortcut: "Ctrl+b"
        menu: root
      }
      ColorButton {
        type: "color"
        color: "green"
        shortcut: "Ctrl+g"
        menu: root
      }
      ColorButton {
        type: "color"
        color: "black"
        shortcut: "Ctrl+n"
        menu: root
      }
    }
    }
    MenuSeparator {
      contentItem: Rectangle {
        implicitWidth: 200
        implicitHeight: 1
//        implicitHeight: 1
//        maxHeight: 1
        color: "#21be2b"
      }
      }
  MenuItem {
    RowLayout {
      anchors.fill: parent
      spacing: 0
      ColorButton {
        type: "underline"
        color: "red"
        shortcut: "Alt+r"
        menu: root
        text: "S"
      }
      ColorButton {
        type: "underline"
        color: "blue"
        shortcut: "Alt+b"
        menu: root
        text: "S"
      }
      ColorButton {
        type: "underline"
        color: "green"
        shortcut: "Alt+g"
        menu: root
        text: "S"

      }
      ColorButton {
        type: "underline"
        color: "black"
        shortcut: "Alt+n"
        menu: root
        text: "S"

      }
    }
  }

  //      }
  //    Button {
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