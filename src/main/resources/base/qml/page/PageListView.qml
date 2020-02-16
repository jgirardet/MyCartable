import QtQuick 2.14
import QtQuick.Controls 2.14

ListView {
  id: lv
  spacing: 10
  clip: true
  property int oldCount
//  onCountChanged: {
//    print("count changed", count)
//    print(count, oldCount)
//
//    if (count - oldCount == 1) {
//      positionViewAtEnd()
//      currentIndex = count - 1
//    }
//    oldCount = count
//  }


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
      ListView.onAdd: {
        print(" on delegate")
      }
    }
  }
  delegate: Component {
    Loader {
      property int curSectionId: page.id
      ListView.onAdd: {
        print("on loader")
      }
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