import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
Rectangle {
  id: base

  /* beautify preserve:start */
  property var model
  /* beautify preserve:end */
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
    model: base.model.pages
    header: Rectangle {
      height: _listView.commonHeight
      color: "blue"
      width: ListView.view.width
      property MouseArea mousearea: headerMouseArea
      property Label label: headerLabel
      Label {
        id: headerLabel
        text: base.model.nom
        anchors.centerIn: parent
      }
      MouseArea {
        id: headerMouseArea
        acceptedButtons: Qt.RightButton
        anchors.fill: parent
        onPressed: {
          if (mouse.buttons == Qt.RightButton) {
            ddb.newPage(model.id)

          }
        }
      }
    }
    headerPositioning: ListView.OverlayHeader
    delegate: Button {
      id: but
      //      objectName: "buttonDelegate"
      text: modelData.titre
      width: ListView.view.width
      height: _listView.commonHeight
      onClicked: {
        print("clicked")
        ddb.currentPage = modelData.id

      }
      //      Component.onCompleted:print(modelData['id'])
    }
  }
}