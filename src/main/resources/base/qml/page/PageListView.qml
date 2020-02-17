import QtQuick 2.14
import QtQuick.Controls 2.14

ListView {

  id: lv
  spacing: 10
  clip: true
  property int oldCount
  currentIndex: 0
  focus: true

  highlightMoveDuration: 1000
  highlightMoveVelocity: -1
  //  cacheBuffer: 500

//  preferredHighlightBegin: 0
//  preferredHighlightEnd: height / 2 + 1000
//  highlightRangeMode: ListView.StrictlyEnforceRange

  onMovementEnded: {print("mouvement ende", indexAt)}

  function onItemAdde(row) {
    currentIndex = row
  }

  Component.onCompleted: {
    model.itemAdded.connect(onItemAdded)
  }
  onCurrentIndexChanged: {
    print(currentIndex)
  }

  onCountChanged: {
    if (count - oldCount == 1) {
      currentIndex = count - 1
    }
    oldCount = count
  }

  Component {
    id: textDelegate
    TextSection {
      sectionId: curSectionId
      base: lv
    }
  }

  Component {
    id: imageDelegate
    AnnotableImage {
      sectionId: curSectionId
      base: lv
    }
  }
  delegate: Component {
    Loader {
      id: load
      property int curSectionId: page.id
      ListView.onAdd: { print("animation !!!!") }

      sourceComponent: switch (page.classtype) {
        case "ImageSection": {
          return imageDelegate
        }

        case "TextSection": {
          return textDelegate
        }
      }

    }
  }
}