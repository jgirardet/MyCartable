import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/actions" as PageActions

ToolButton {
    id: control

    property string sectionName
    property int targetIndex
    property var dialog
    property bool appendMode
    property QtObject page

    enabled: page
    icon.color: enabled ? "transparent" : ddb.colorPageToolBar
    visible: enabled
    onPageChanged: {
        if (action)
            action.page = page;

    }

    PageActions.ActionToolTip {
        visible: hovered
        text: action.tooltip
        shortcut: action.shortcut ?? ""
    }

    background: Rectangle {
        //    width: 40
        implicitWidth: 40
        implicitHeight: 40
        //    height: 40
        color: Qt.darker(ddb.colorPageToolBar, control.enabled && control.hovered ? 1.5 : 1)
    }

}
