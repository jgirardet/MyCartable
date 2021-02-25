import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/js/stringUtils.mjs" as StringUtils

/*
TextArea connected to a QUndoStack
===================================

Disable default undostack capturing undo/redo command.
Non white space character are grouped.

Required Properties
--------------------

QtObject txtfield: binding to a string Property. ex : txtfield: mycontroler.title

QUndoStack undostack: binding to connected undostack. ex: undostack: mycontroler.myQundostack

Optional Properties
-------------------

int undoDelay: timeout b for grouping sequential keypressed. defaut = 300ms.

Virtual Method
---------------

void setText(): should be used instead of onTextChanged.

*/
TextArea {
    id: root

    required property string txtfield
    required property QtObject undostack
    property int undoDelay: 300
    property alias timer: timertext
    property bool _spacePending: false

    /* SetText
    Virtual method called when text is changed
    */
    function setText() {
    }

    selectByMouse: true
    onTxtfieldChanged: {
        if (text != txtfield) {
            // calculate the new cursor position
            let [curStart, curEnd] = StringUtils.diff(text, txtfield);
            let sStart, sEnd;
            let diff = curEnd - curStart;
            if (length > txtfield.length) {
                sStart = sEnd = curStart; // newer text is shorter
            } else {
                if (diff > 1) {
                    sStart = curStart;
                    sEnd = curEnd;
                } else {
                    sStart = sEnd = curEnd;
                }
            }
            text = txtfield;
            select(sStart, sEnd);
            forceActiveFocus();
        }
    }
    onTextChanged: {
        if (text != txtfield) {
            if (_spacePending)
                timertext.triggered();
            else
                timertext.restart();
        }
    }
    Keys.onPressed: {
        if (event.matches(StandardKey.Undo))
            root.undostack.undo();
        else if (event.matches(StandardKey.Redo))
            root.undostack.redo();
        if (event.text) {
            if (event.text.trim() === '') {
                // detect white space
                timertext.triggerPending();
                _spacePending = true;
            }
        }
    }

    Timer {
        id: timertext

        function triggerPending() {
            if (timertext.running)
                timertext.triggered();

        }

        interval: parent.undoDelay
        repeat: false
        onTriggered: parent.setText()
    }

}
