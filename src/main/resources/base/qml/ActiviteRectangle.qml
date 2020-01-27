import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12


Rectangle {
        id: base
        property QtObject ddb
        property alias headerText: _listView.headerText
        property alias headerColor: _listView.headerColor
        property int activiteIndex
        property alias model: _listView.model
        Layout.preferredHeight: ddb.getLayoutSizes("preferredActiviteHeight")
        Layout.minimumHeight: ddb.getLayoutSizes("minimumActiviteHeight")
        Layout.maximumHeight: Layout.preferredHeight
        Layout.fillWidth: true

        ActiviteListView {
            id: _listView
            objectName: "_listView"
            anchors.fill: parent
            onItemClicked: base.ddb.currentPage = idPage


        }




}