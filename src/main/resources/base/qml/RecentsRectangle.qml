import QtQuick 2.12
import QtQuick.Controls 2.12

Rectangle {
    id: base
    color: "orange"
    height: baseItem.height
    width: lateralsColumnWidth
    property QtObject ddb

    Column {
        id : recentsColumn
        height: parent.height
        width: parent.width
        spacing: 5


        RoundButton {
            id: recentsHeader
            objectName: "recentsHeader"
            height: root.headersHeight
            width: root.lateralsColumnWidth
            text: base.ddb.currentMatiere //"Récents"
            radius: 10
         }

        RecentsListView {
            id: _recentsListView
            objectName: "_recentsListView"
            model: recentsModel
            onItemClicked: base.ddb.recentsItemClicked(id)

        }

    }
}