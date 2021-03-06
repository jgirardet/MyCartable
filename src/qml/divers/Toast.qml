// Popup will be closed automatically in 2 seconds after its opened

import QtQuick 2.15
import QtQuick.Controls 2.15

Popup {
    id: popup

    property string msg: ""
    property color bgcolor: "yellow"
    property color txtcolor: "red"
    property alias interval: popupClose.interval

    function showToast(message) {
        toast.msg = message;
        toast.open();
    }

    closePolicy: Popup.CloseOnPressOutside
    onOpened: popupClose.start()

    Text {
        id: message

        anchors.centerIn: parent
        font.pointSize: 12
        color: popup.txtcolor
        text: popup.msg
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
