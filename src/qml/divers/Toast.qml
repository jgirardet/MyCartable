// Popup will be closed automatically in 2 seconds after its opened

import QtQuick 2.14
import QtQuick.Controls 2.14

Popup {
    id: popup

    property string msg
    property color bgcolor: "yellow"
    property color txtcolor: "red"

    focus: true
    closePolicy: Popup.CloseOnPressOutside
    onOpened: popupClose.start()

    Text {
        id: message

        anchors.centerIn: parent
        font.pointSize: 12
        color: popup.txtcolor
        text: popup.msg
        onTextChanged: {
            print(text);
        }
    }

    Timer {
        id: popupClose

        interval: 2000
        onTriggered: popup.close()
    }

    background: Rectangle {
        implicitWidth: 200
        implicitHeight: 60
        color: popup.bgcolor
    }

}
