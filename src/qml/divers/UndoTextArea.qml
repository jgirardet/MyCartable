import QtQuick 2.15
import QtQuick.Controls 2.15

TextArea {
    // premier retour en arrière, il faut enregistrer la dernière position
    //            _pendingFrappe=true

    id: root

    required property QtObject connectedStack
    property string bindedText
    property int undoDelay: 300
    property var _stack: []
    property int _cursorStack: 0
    property bool _bindUpdateEnabled: true
    property bool _pendingFrappe: true
    property var _tmpcurs: null

    function capture_undo_redo(event) {
        if ((event.key == Qt.Key_Z) && (event.modifiers & Qt.ControlModifier)) {
            event.accepted = true;
            return true;
        }
    }

    function capture_paste(event) {
        if ((event.key == Qt.Key_V) && (event.modifiers & Qt.ControlModifier)) {
            event.accepted = true;
            return true;
        }
    }

    function capture_cut(event) {
        if ((event.key == Qt.Key_X) && (event.modifiers & Qt.ControlModifier)) {
            event.accepted = true;
            return true;
        }
    }

    function handle_paste() {
        _addToStack();
        paste();
    }

    function handle_cut() {
        _addToStack();
        cut();
    }

    function handle_undo_redo(event) {
        if (event.modifiers & Qt.ShiftModifier)
            redo();
        else
            undo();
    }

    function redo() {
        print("»»» début redo: " + "cursorstack=" + _cursorStack);
        if (!_cursorStack)
            return ;

        _bindUpdateEnabled = false;
        connectedStack.redo();
        _cursorStack--;
        _moveCursorWithStack();
        _bindUpdateEnabled = true;
        print("»»» Fin redo: ");
    }

    function undo() {
        print("»»» Début undo: " + "cursorstack=" + _cursorStack);
        if (timertext.running)
            timertext.triggered();

        //        while (timertext.running){}
        _bindUpdateEnabled = false;
        if (!_cursorStack)
            _addToStack();

        connectedStack.undo();
        _cursorStack++;
        _moveCursorWithStack();
        _bindUpdateEnabled = true;
        print("»»» Fin undo: ");
    }

    function _moveCursorWithStack() {
        print(_stack.length - _cursorStack);
        let pos = _stack[_stack.length - 1 - _cursorStack];
        print("movecursor to : ", JSON.stringify(pos), JSON.stringify(_stack), _cursorStack);
        select(pos.start, pos.end);
    }

    function _addToStack(start = selectionStart, end = selectionEnd) {
        if (_cursorStack) {
            // event est text mais en cours de undo, donc on invalide tout le redo restant
            _stack = _stack.slice(0, _stack.length - _cursorStack - 1);
            _cursorStack = 0;
        }
        _stack.push({
            "start": start,
            "end": end
        });
    }

    function _submitPending() {
        _addToStack(_tmpcurs.start, _tmpcurs.end);
        setText();
        _tmpcurs = null;
    }

    function _triggerPending() {
      if (timertext.running)
                  timertext.triggered();
    }

    onTextChanged: {
        print("»»» début onTextChanged: ", bindedText, text, Boolean(selectedText), selectedText, selectionStart, selectionEnd);
        if (text != bindedText && _bindUpdateEnabled && !_tmpcurs)
            setText();
        else if (_tmpcurs)
            timertext.restart();
        print("»»» fin onTextChanged", bindedText, text);
    }
    onBindedTextChanged: {
        print("»»» début onBindedText Changed", bindedText, text);
        if (bindedText != text)
            text = bindedText;

        print("»»» fin onBindedText Changed", bindedText, text);
    }
    Component.onCompleted: {
        print("completed debut");
        text = bindedText;
        print("completed fin");
    }
    Keys.onPressed: {
        if (capture_undo_redo(event)) {
            handle_undo_redo(event);
        } else if (capture_paste(event)) {
            handle_paste();
        } else if (capture_cut(event)) {
            handle_cut();
        } else if (event.text) {
            if (event.text.trim() === '') {
                //detect white space
                _triggerPending()
                _addToStack()

                print("");
            } else {
            if (!_tmpcurs)
                _tmpcurs = {
                "start": selectionStart,
                "end": selectionEnd
            };
            }
            //            if (
            //_pendingFrappe) {
            //            }
            //            _addToStack();

        } else if (event.Key == Qt.Key_Backspace || event.Key == Qt.Key_Delete) {
            _addToStack();
        }
    }

    Timer {
        //      onTriggered:

        id: timertext

        interval: root.undoDelay
        repeat: false
        onTriggered: _submitPending()
    }

}
