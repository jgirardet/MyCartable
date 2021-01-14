import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Row {
    id: root

    required property Item lexique
    property alias items: repeater

    function triggerAdd() {
        let trads = [];
        for (const n of Array(repeater.count).keys()) {
            let it = repeater.itemAt(n);
            if (it.text)
                trads.push({
                "locale": it.locale,
                "content": it.text
            });

            it.clear();
        }
        let res = lexique.addLexon(trads);
    }

    Database {
        id: database
    }

    Repeater {
        //            Keys.rightPressed: print("right")
        //            Keys.onRightPressed: root.navigate()

        id: repeater

        model: lexique.model.locales

        delegate: TextField {
            id: label

            property string locale: modelData

            width: database.getConfig("lexiqueColumnWidth")
            text: ""
            color: 'black'
            font.pointSize: 20
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            onAccepted: root.triggerAdd()
            KeyNavigation.right: index < repeater.count - 1 ? repeater.itemAt(index + 1) : repeater.itemAt(0)
            KeyNavigation.left: index > 0 ? repeater.itemAt(index - 1) : repeater.itemAt(repeater.count - 1)

            background: Rectangle {
                border.width: 1
                anchors.fill: parent
                color: "lightgrey"
            }

        }

    }

}
