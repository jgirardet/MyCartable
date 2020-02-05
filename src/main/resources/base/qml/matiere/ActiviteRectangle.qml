import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
Rectangle {
  id: base
  property alias headerText: _listView.headerText
  property alias headerColor: _listView.headerColor
  property alias model: _listView.model
  Layout.preferredHeight: ddb.getLayoutSizes("preferredActiviteHeight")
  Layout.minimumHeight: ddb.getLayoutSizes("minimumActiviteHeight")
  Layout.maximumHeight: Layout.preferredHeight
  Layout.fillWidth: true
  ListView {
    id: _listView
    objectName: "_listView"
    anchors.fill: parent
    clip: true
    property int commonHeight: 30
    property string headerText: "header"
    property string headerColor: "blue"
    header: Rectangle {
      objectName: "headerRectangle"
      height: _listView.commonHeight
      color: headerColor
      width: ListView.view.width
      Label {
        text: headerText
        objectName: "headerLabel"
        anchors.centerIn: parent
      }
    }
    headerPositioning: ListView.OverlayHeader
    delegate: Button {
      id: but
      objectName: "buttonDelegate"
      text: modelData.titre
      width: ListView.view.width
      height: _listView.commonHeight
      onClicked: {
        ddb.currentPage = modelData.id

      }
    }
  }
}