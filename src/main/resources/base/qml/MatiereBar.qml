import QtQuick 2.12
import QtQuick.Controls 2.12

TabBar {
    id: bar
    width: 500

    Repeater {
        id: rep
        model:  5

        TabButton {
            text: modelData
//            property  int lid: modelData['id']
//            width: Math.max(100, bar.width / 5)
//            onClicked: console.log(lid)
        }

    }

}