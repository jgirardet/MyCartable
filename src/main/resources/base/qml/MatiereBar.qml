import QtQuick 2.12
import QtQuick.Controls 2.12

TabBar {
    id: bar
    width: parent.width

    Repeater {
        id: rep
        model:  ddb.matiereNoms

        TabButton {
            text: modelData['nom']
            property  int lid: modelData['id']
            width: Math.max(100, bar.width / 5)
            onClicked: console.log(lid)
        }

    }

}