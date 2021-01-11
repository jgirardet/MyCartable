import Qt.labs.platform 1.1

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
