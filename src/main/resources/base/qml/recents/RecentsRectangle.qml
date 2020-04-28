import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
Rectangle {
  id: base
  //  color: Qt.rgba(130/255, 134/255, 138/255 , 1)
  color: ddb.colorFond
  property alias listview: recentsListView
  Column {
    id: recentsColumn
    anchors.fill: parent
    spacing: 5
    //    RoundButton {
    //      id: recentsHeader
    //      objectName: "recentsHeader"
    //      height: ddb.getLayoutSizes("preferredHeaderHeight")
    //      width: parent.width
    //      text: "Récents"
    //      radius: 10
    //    }
    RecentsListView {
      id: recentsListView
      model: ddb.recentsModel
      onItemClicked: ddb.recentsItemClicked(id, matiere)
    }
  }
}