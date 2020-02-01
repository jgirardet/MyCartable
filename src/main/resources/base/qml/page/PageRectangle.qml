import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.14
Rectangle {
  id: base
  color: "steelblue"
  ColumnLayout {
    anchors.fill: parent
    spacing: 5
    PageToolBar {
      id: pageToolBar
      width: parent.width
      height: ddb.getLayoutSizes("preferredHeaderHeight")
      onNouveau: ddb.newPage(2)
    }
    TextField {
      text: ddb.currentTitre
      id: _currentTitreTextField
      readOnly: ddb.currentMatiere == 0 ? true : false
      Layout.fillWidth: true
      Layout.preferredHeight: 50
      //                    onTextChanged: ddb.
      //                    Component.onCompleted: text.connect(ddb.currentTitre)
      //                    }
    }
    Binding {
      target: ddb;property: "currentTitre";value: _currentTitreTextField.text
    }
    PageListView {
      Layout.fillWidth: true
      Layout.fillHeight: true
      model: ddb.pageModel
    }
  }
}