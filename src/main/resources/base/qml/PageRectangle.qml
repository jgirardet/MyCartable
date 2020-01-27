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
                    width: parent.width
                    height: ddb.getLayoutSizes("preferredHeaderHeight")
                    onNouveau: ddb.newPage(2)
                   }
                Rectangle {
                    width: parent.width
                    height: parent.height -pageToolBar.height -parent.spacing
                    color: "green"
                    PageListView {
                      height: parent.height
                      width: parent.width
//                        model:
//                            [
//                                {type:"texte", content: "omkmok"}
//                            ]
                        model:base.ddb.pageModel
//                        model:base.ddb.fakeModel()
                        }
                }
            }
}