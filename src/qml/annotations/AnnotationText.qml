import QtQuick 2.15
import QtQuick.Controls 2.15

TextArea {
    // casse le binding mais evite le loop, donc on laisse pour le moment

    id: root

    property var referent
    property QtObject annot
    property var menu: uiManager.menuFlottantAnnotationText
    property int pointSizeStep: 1
    property int moveStep: 5
    property int fontSizeFactor: annot.pointSize ? annot.pointSize : 0 //uiManager.annotationCurrentTextSizeFactor

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

    text: annot.text
    onTextChanged: annot.text = text
    //size and pos
    height: contentHeight
    padding: 0
    width: contentWidth + 5
    focus: parent.focus
    color: annot.fgColor
    font.underline: annot.underline
    font.pixelSize: (referent.height / fontSizeFactor) | 0
    selectByMouse: true
    Component.onCompleted: {
        if (!annot.pointSize)
            fontSizeFactor = uiManager.annotationCurrentTextSizeFactor;

        forceActiveFocus();
        timerRemove.running = true;
    }
    onFontSizeFactorChanged: {
        if (annot.pointSize == fontSizeFactor)
            return ;

        // attention on stock fontSizeFactor dans du pointSize :le nom dans la ddb est nul :-)
        annot.pointSize = root.fontSizeFactor;
        uiManager.annotationCurrentTextSizeFactor = root.fontSizeFactor;
    }
    onFocusChanged: {
        if (focus)
            cursorPosition = text.length;
        else if (!text)
            timerRemove.running = true;
    }
    Keys.onPressed: {
        if ((event.key == Qt.Key_Plus) && (event.modifiers & Qt.ControlModifier)) {
            root.fontSizeFactor -= pointSizeStep;
            event.accepted = true;
        } else if ((event.key == Qt.Key_Minus) && (event.modifiers & Qt.ControlModifier)) {
            root.fontSizeFactor += pointSizeStep;
            event.accepted = true;
        } else if ([Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down].includes(event.key) && (event.modifiers & Qt.ControlModifier)) {
            move(event.key);
            event.accepted = true;
        }
    }

    Timer {
        id: timerRemove

        objectName: "timerRemove"
        interval: 3000
        running: false
        repeat: false
        onTriggered: {
            if (text == "")
                root.referent.model.remove(index);

        }
    }

    background: Rectangle {
        anchors.fill: parent
        color: annot.bgColor
        border.color: parent.focus ? "#21be2b" : "transparent"
        opacity: referent.section.annotationTextBGOpacity
    }

}
