import QtQuick 2.14
import QtQuick.Controls 2.14

ListView {
  id: lv
  spacing: 10
  clip: true
  function enBas() {
                print("dans en bas")
                var newIndex = count - 1 // last index
                positionViewAtEnd()
//                positionViewAtIndex(count, ListView.Contain)
//                currentIndex = newIndex
            }
    property int oldCount
    onCountChanged: {
      if (count - oldCount == 1) {
        enBas()
      }
      oldCount = count

    }

//  Component.onCompleted: {
//    onCountChanged.connect(enBas)
//  }
  //  ListView.onAdd: {
                        //                var newIndex = count - 1 // last index
                        ////                positionViewAtEnd()
                        //                positionViewAtIndex(count-1, ListView.Beginning)
                        //                currentIndex = newIndex
                        //            }


  //positionViewAtIndex(lv.count -2, ListView.Beginning)

  //  MouseArea {
  //    anchors.fill: parent
  //    onClicked: positionViewAtIndex(lv.count -1, ListView.Beginning)
  //  }

  //  Binding on currentIndex {
  //     when: ddb.currentPageIndexChanged
  //    value: ddb.currentPageIndex
  // }

  //   onCurrentIndexChanged: {
  //   positionViewAtIndex(currentIndex +1, ListView.Beginning)
  //  print(currentIndex)}

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


//      Component.onCompleted: {
//        console.log("This prints just fine!")
//        lv.positionViewAtEnd()
//      }
    }
  }

  delegate: Component {
    Loader {
      property int curSectionId: page.id


      sourceComponent: switch (page.classtype)
       {
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