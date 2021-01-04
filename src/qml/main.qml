import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/divers"
import "qrc:/qml/layouts"

ApplicationWindow {
    id: root

    property alias mainItem: mainitem

    function reload() {
        root.title = get_title();
        mainItem.clear();
    }

    function get_title() {
        let an = database.getConfig("annee");
        return "MyCartable: année " + an + "/" + (an + 1);
    }

    width: 1100
    height: 600
    visible: true
    Component.onCompleted: {
        root.title = get_title();
    }

    Database {
        id: database
    }

    MainMenuBar {
        id: mainmenubar

        mainItem: mainitem
        base: root
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
    }

    SplitLayout {
        id: mainitem

        anchors.top: mainmenubar.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        layouts: JSON.parse(database.getConfig("layouts"))
        initDataModel: ["classeur"]
    }

}
