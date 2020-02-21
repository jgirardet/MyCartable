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
    }
    PageTitre {
      id: titre
      page: pagelistview
    }

    PageListView {
      id: pagelistview
      Layout.fillWidth: true
      Layout.fillHeight: true
      model: ddb.pageModel
    }
  }
}