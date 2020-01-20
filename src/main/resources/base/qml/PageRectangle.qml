import QtQuick 2.12
import QtQuick.Controls 2.12


 Rectangle {
            id: base
            color: "red"
            property QtObject ddb


            Column {
                anchors.fill: parent
                spacing: 5

                PageToolBar {
                    id: pageToolBar
                    width: base.width
                    height: root.headersHeight
                    onNouveau: _itemDispatcher.newPage(2)
                   }
                Rectangle {
                    width: parent.width
                    height: parent.height -pageToolBar.height -parent.spacing
                    color: "green"
                    PageListView{model:[1,2,3,4,5,]}
                }
            }
}