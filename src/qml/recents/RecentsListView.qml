import QtQuick 2.12
import QtQuick.Controls 2.12
ListView {
  id: root
  signal itemClicked(int id, int matiere)
  headerPositioning: ListView.OverlayHeader
  spacing: 5
  height: parent.height
  width: parent.width
  clip: true
  delegate: RoundButton {
    id: recentButton
    objectName: "recentButton"
    height: contentItem.contentHeight + 20
    radius: 10
    Component.onCompleted: {
      textInitialPosition = moving_text.x
    }
    property int textInitialPosition
    property int trajet: moving_text.contentWidth - recentButton.width + 10
    property int dureeMove: trajet > 0 ? trajet * 20 : 0
    contentItem: Text {
      id: moving_text
      text: modelData.titre
      font.family: "Verdana"
      elide: Text.ElideRight

      NumberAnimation on x {
        id: moveTextLeft
        from: textInitialPosition
        to: -trajet
        loops: 1 // Animation.Infinite
        duration: dureeMove
        running: false
        onFinished: {
          //          restart()
          moveTextRight.restart()
        }
      }
      NumberAnimation on x {
        id: moveTextRight
        from: moving_text.x
        to: textInitialPosition
        loops: 1 // Animation.Infinite
        duration: dureeMove
        running: false
        onFinished: {
          pauseTimer.restart()

        }
      }
      Timer {
        id: pauseTimer
        interval: 1000
        running: false
        repeat: false
        onTriggered: moveTextLeft.restart()
      }
    }
    onHighlightedChanged: {
      if (highlighted) {
        moving_text.elide = Text.ElideNone
        moveTextLeft.restart()
        //        textInitialPosition = moving_text.x + leftPadding
      } else {
        moving_text.elide = Text.ElideRight
        moveTextLeft.stop()
        moveTextRight.stop()
        moving_text.x = textInitialPosition
      }
    }
    highlighted: hovered
    background: Rectangle {
      id: back
      color: modelData.matiereBgColor ? modelData.matiereBgColor : "white"
      anchors.fill: parent
      radius: 10
      border.width: highlighted ? 3 : 1
      //      border.color: modelData == null ? "white" : highlighted ? Qt.darker(modelData.bgColor, 3) : Qt.lighter(modelData.bgColor, 10)
    }
    width: ListView.view.width
    onClicked: ListView.view.itemClicked(modelData.id, modelData.matiere)
  }
  // TODO: tester tout ça
}