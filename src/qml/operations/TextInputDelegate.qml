import QtQuick 2.14
import QtQuick.Controls 2.14
import "qrc:/qml/divers"

TextField {
    id: input

    property QtObject model: parent.model

    function moreKeys(event) {
    }

    focus: parent.GridView.isCurrentItem
    anchors.fill: parent
    text: display
    readOnly: model.readOnly(index)
    cursorDelegate: cursorComp
    onFocusChanged: {
        if (focus && !readOnly)
            parent.GridView.view.currentIndex = index;

    }
    Keys.onPressed: {
        var isMove = [Qt.Key_Up, Qt.Key_Left, Qt.Key_Down, Qt.Key_Right].includes(event.key);
        var numPressed = [Qt.Key_0, Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5, Qt.Key_6, Qt.Key_7, Qt.Key_8, Qt.Key_9].includes(event.key);
        var delPressed = [Qt.Key_Backspace, Qt.Key_Delete].includes(event.key);
        if (isMove) {
            model.moveCursor(index, event.key);
            event.accepted = true;
        } else if (numPressed) {
            edit = event.text;
            event.accepted = true;
        } else if (delPressed) {
            edit = "";
            event.accepted = true;
        } else {
            moreKeys(event);
        }
    }

    Component {
        id: cursorComp

        Item {
        }

    }

    validator: IntValidator {
        bottom: 0
        top: 9
    }

    background: BorderRectangle {
        //    color: input.parent.color
        color: input.focus ? "yellow" : root.color
        borderColor: model.isResultLine(index) ? "black" : input.parent.color
        borderTop: -2
    }

}
