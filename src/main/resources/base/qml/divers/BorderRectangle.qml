import QtQuick 2.14

Rectangle {
  anchors.fill: parent
  color: "white"
  property alias borderColor: borderItem.color
  property alias borderTop: borderItem.anchors.topMargin
  property alias borderBottom: borderItem.anchors.bottomMargin
  property alias borderLeft: borderItem.anchors.leftMargin
  property alias borderRight: borderItem.anchors.rightMargin
  Rectangle {
    id: borderItem
    z:-1
    anchors {
      fill: parent
  }
}
}
