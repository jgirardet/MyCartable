import QtQuick 2.14
import QtQuick.Controls 2.14


TableView {
        id: root
        property int position
        property int sectionId
//        anchors.fill: parent
        width: 300
        height: 300
        columnSpacing: 1
        rowSpacing: 1
        delegate: Rectangle {
            implicitWidth: 20
            implicitHeight: 20
            color: "red"
            border.width: 1
            TextInput {
              anchors.fill: parent
                text: model.display
            }
            Component.onCompleted:{
            print(model.display)


            }
          }
    }