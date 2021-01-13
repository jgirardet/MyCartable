import QtQuick 2.15
import QtQuick.Controls 2.15

HorizontalHeaderView {
    id: root

    delegate: Label {
        //        height: contentHeight + 50
        text: display
        color: '#aaaaaa'
        font.pointSize: 20
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter

        MouseArea {
            anchors.fill: parent
            onClicked: syncView.model.doSort(index)
        }

    }

}
