import QtQuick 2.15

Rectangle {
    property alias borderColor: borderItem.color
    property alias borderTop: borderItem.anchors.topMargin
    property alias borderBottom: borderItem.anchors.bottomMargin
    property alias borderLeft: borderItem.anchors.leftMargin
    property alias borderRight: borderItem.anchors.rightMargin

    anchors.fill: parent
    color: "white"

    Rectangle {
        id: borderItem

        z: -1

        anchors {
            fill: parent
        }

    }

}
