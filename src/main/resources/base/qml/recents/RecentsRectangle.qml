import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
Rectangle {
  id: base
  color: "orange"
  Column {
    id: recentsColumn
    anchors.fill: parent
    spacing: 5
    RoundButton {
      id: recentsHeader
      objectName: "recentsHeader"
      height: ddb.getLayoutSizes("preferredHeaderHeight")
      width: parent.width
      text: "Récents"
      radius: 10
    }
    RecentsListView {
      id: recentsListView
      objectName: "recentsListView"
      model: ddb.recentsModel
      onItemClicked: ddb.recentsItemClicked(id, matiere)
    }
  }
}