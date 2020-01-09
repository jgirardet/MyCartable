import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Window 2.12

ApplicationWindow {
    id: root
    width: 800
    height: 600
    visible: true



    header : MainMenuBar {
            id: mainMenuBar

    }

    MatiereBar {
        id: matiereBar
        anchors.top: mainMenuBar.bottom
    }

    Label {
        anchors.top: matiereBar.bottom
        text: ddb.matiereTest()
    }







 }