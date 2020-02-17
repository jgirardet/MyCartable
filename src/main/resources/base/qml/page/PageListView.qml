import QtQuick 2.14
import QtQuick.Controls 2.14

BasePageListView {
  id: lv
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
//
//ListView {
//
//  id: lv
//  spacing: 10
//  clip: true
//  currentIndex: 0
//  focus: true
//
//  highlightMoveDuration: 1000
//  highlightMoveVelocity: -1
//  //  cacheBuffer: 500
//
////  preferredHighlightBegin: 0
////  preferredHighlightEnd: height / 2 + 1000
////  highlightRangeMode: ListView.StrictlyEnforceRange
//
//  onMovementEnded: {print("mouvement ende", indexAt)}
//
//  function onInsertRows(modelIndex, row, col) {
//    currentIndex = row
//  }
//
//
//
//  Component.onCompleted: {
//    model.rowsInserted.connect(onInsertRows)
//  }
//  onCurrentIndexChanged: {
//    print(currentIndex)
//  }
//
//
//  Component {
//    id: textDelegate
//    TextSection {
//      sectionId: curSectionId
//      base: lv
//    }
//  }
//
//  Component {
//    id: imageDelegate
//    AnnotableImage {
//      sectionId: curSectionId
//      base: lv
//    }
//  }
//  delegate: Component {
//    Loader {
//      id: load
//      property int curSectionId: page.id
//
//      sourceComponent: switch (page.classtype) {
//        case "ImageSection": {
//          return imageDelegate
//        }
//        case "TextSection": {
//          return textDelegate
//        }
//      }
//
//    }
//  }
//}