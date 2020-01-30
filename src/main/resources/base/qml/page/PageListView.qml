import QtQuick 2.12
import QtQuick.Controls 2.12
import Qt.labs.qmlmodels 1.0


ListView {
    id: lv

    spacing : 10
    clip: true

//    DelegateChooser {
//        id: chooser
//        role: "type"
////        DelegateChoice { delegate: Rectangle {color: "blue"; height: 30; width: 200 }}
//        DelegateChoice { roleValue: "texte"; delegate: PageTexteDelegate { text:texte.content } }
////        DelegateChoice { roleValue: "switch"; SwitchDelegate { ... } }
////        DelegateChoice { roleValue: "swipe"; SwipeDelegate { ... } }
//    }
//    delegate: chooser
    Component {
        id: texteDelegate
        PageTexteDelegate  { text: datas.content ; width: lv.width}
    }
    Component {
        id: imageDelegate
        PageImageDelegate { section: datas}
    }
    delegate: Component {
        Loader {
            property var datas: display
            sourceComponent: switch(display.type) {
                case "texte": return texteDelegate
                case "image": return imageDelegate
            }
        }
    }
}