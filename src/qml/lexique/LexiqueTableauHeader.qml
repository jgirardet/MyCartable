import QtQuick 2.15
import QtQuick.Controls 2.15

HorizontalHeaderView {
    id: root

    required property Item lexique
    required property int columnWidth

    columnWidthProvider: () => {
        return columnWidth;
    }
    rowHeightProvider: () => {
        return 50;
    }
    model: lexique.model

    delegate: Label {
        text: display
        color: '#aaaaaa'
        font.pointSize: 14
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        Component.onCompleted: {
            root.contentX = 1;
            root.returnToBounds();
        }

        MouseArea {
            anchors.fill: parent
            onClicked: lexique.doSort(index)
        }

    }

}
