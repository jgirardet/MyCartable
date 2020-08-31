import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs 1.3

ColorDialog {
    id: colordialog

    property var target

    function ouvre(tg) {
        target = tg;
        open();
    }

    onAccepted: {
        target.startcolor = color;
    }
    modality: Qt.WindowModal
}
