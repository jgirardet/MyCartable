import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ToolTip {
    id: ttip

    property string shortcut

    contentItem: ColumnLayout {
        spacing: 0

        Text {
            text: ttip.text
            Layout.fillWidth: true
            color: "black"
            font.pointSize: 8
            horizontalAlignment: Text.AlignHCenter
        }

        Text {
            text: shortcut.split("+").join(" + ")
            Layout.fillWidth: true
            font.pointSize: 8
            horizontalAlignment: Text.AlignHCenter
            color: "black"
            visible: text != ""
        }

    }

    background: Rectangle {
        color: "white"
        border.color: "black"
    }

}
