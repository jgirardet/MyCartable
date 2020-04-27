import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.14
import "qrc:/qml/menu"
Rectangle {
  id: base
  color: Qt.rgba(98 / 255, 105 / 255, 123 / 255, 1)
  ColumnLayout {
    anchors.fill: parent
    spacing: 10
    PageToolBar {
      id: pageToolBar
      Layout.fillWidth: true
      height: ddb.getLayoutSizes("preferredHeaderHeight")
    }

    Rectangle {
        Layout.preferredWidth: parent.width -20
        Layout.preferredHeight: 50
        Layout.alignment: Qt.AlignHCenter
        color: "transparent"

      PageTitre {
        id: titre
        anchors.fill: parent
        page: pagelistview
      }
    }
    Rectangle {
        Layout.fillWidth: true
        Layout.fillHeight: true
        color: "transparent"
        radius: 10
      PageListView {
        anchors.fill: parent
        id: pagelistview
        model: ddb.pageModel
      }
    }
//    PageListView {
//      id: pagelistview
//      Layout.fillWidth: true
//      Layout.fillHeight: true
//      model: ddb.pageModel
//    }

  }

  Component.onCompleted: {
    var newComp = Qt.createComponent("qrc:/qml/menu/MenuFlottantStabylo.qml")
    if (newComp.status == Component.Ready) {
      uiManager.menuFlottantStabylo = newComp.createObject(base)
    } else {
      print(newComp.errorString())
    }
    var newComp = Qt.createComponent("qrc:/qml/menu/MenuFlottantText.qml")
    if (newComp.status == Component.Ready) {
      uiManager.menuFlottantText = newComp.createObject(base)
    } else {
      print(newComp.errorString())
    }
    var newComp = Qt.createComponent("qrc:/qml/menu/MenuFlottantTableau.qml")
    if (newComp.status == Component.Ready) {
      uiManager.menuFlottantTableau = newComp.createObject(base)
    } else {
      print(newComp.errorString())
    }
  }

}