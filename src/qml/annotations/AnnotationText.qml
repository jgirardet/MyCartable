import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/menu"

TextArea {
    id: root

    property var referent
    property QtObject annot
    property alias menu: menuFlottantAnnotationText
    property int pointSizeStep: 1
    property int moveStep: 5
    property int fontSizeFactor: annot && annot.pointSize ? annot.pointSize : 0
    property bool key_accepted: false // true pour le chargement initial
    property  int modelIndex:index

    function move(key) {
        if (key == Qt.Key_Left)
            parent.move(-moveStep, 0);
        else if (key == Qt.Key_Right)
            parent.move(moveStep, 0);
        else if (key == Qt.Key_Up)
            parent.move(0, -moveStep);
        else if (key == Qt.Key_Down)
            parent.move(0, moveStep);
    }

    function checkPointIsNotDraw(mx, my) {
        return false;
    }

    function _place_cursor(len_bak, curs_bak) {
        if (length > len_bak)
            cursorPosition = curs_bak + 1;
        else
            cursorPosition = curs_bak - 1;
    }

    onTextChanged: {
        // on ne sauvegarde pas (pas de creation de command) si c un undo/redo/initial load
        if (key_accepted)
            annot.set(modelIndex, {
            "text": text
        }, "frappe");

        key_accepted = false;
    }
    height: contentHeight
    padding: 0
    width: contentWidth + 5
    focus: parent.focus
    color: annot ? annot.fgColor : "transparent"
    font.underline: annot ? annot.underline : false
    font.pixelSize: (referent.height / fontSizeFactor) | 0
    selectByMouse: true
    Component.onCompleted: {
        if (!annot.pointSize)
            fontSizeFactor = annot.annotationCurrentTextSizeFactor;

        text = annot.text;
    }
    onFontSizeFactorChanged: {
        if (annot.pointSize == fontSizeFactor)
            return ;

        // attention on stock fontSizeFactor dans du pointSize :le nom dans la ddb est nul :-)
        annot.pointSize = root.fontSizeFactor;
        annot.annotationCurrentTextSizeFactor = root.fontSizeFactor;
    }
    onFocusChanged: {
        if (focus)
            cursorPosition = text.length;
        else if (!text)
            {}
    }
    Keys.onPressed: {
        if ((event.key == Qt.Key_Z) && (event.modifiers & Qt.ControlModifier)) {
            let curs_bak = cursorPosition;
            let len_bak = length;
            if (event.modifiers & Qt.ShiftModifier) {
                if (annot.undoStack.canRedo) {
                    annot.undoStack.redo();
                    _place_cursor(len_bak, curs_bak);
                }
            } else {
                if (annot.undoStack.canUndo) {
                    annot.undoStack.undo();
                    _place_cursor(len_bak, curs_bak);
                }
            }
            event.accepted = true;
        } else if ((event.key == Qt.Key_Plus) && (event.modifiers & Qt.ControlModifier)) {
            root.fontSizeFactor -= pointSizeStep;
            event.accepted = true;
        } else if ((event.key == Qt.Key_Minus) && (event.modifiers & Qt.ControlModifier)) {
            root.fontSizeFactor += pointSizeStep;
            event.accepted = true;
        } else if ([Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down].includes(event.key) && (event.modifiers & Qt.ControlModifier)) {
            move(event.key);
            event.accepted = true;
        } else if (event.text) {
            key_accepted = true;
        }
    }

    Connections {
        function onTextChanged() {
            if (text != annot.text)
                text = annot.text;
                // annot.set(modelIndex, {"text":text}, "frappe");

        }

        target: annot
    }

    MenuFlottantAnnotationText {
        id: menuFlottantAnnotationText
    }

    background: Rectangle {
        anchors.fill: parent
        color: annot ? annot.bgColor : "transparent"
        border.color: parent.focus ? "#21be2b" : "transparent"
        opacity: referent.section.annotationTextBGOpacity
    }

}
