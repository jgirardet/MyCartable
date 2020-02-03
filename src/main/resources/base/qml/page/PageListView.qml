import QtQuick 2.12
import QtQuick.Controls 2.12
import Qt.labs.qmlmodels 1.0
ListView {
  id: lv
  spacing: 10
  clip: true

  Component {
    id: texteDelegate
    TextSection {
//      text: datas.content;width: lv.width
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
      /* beautify preserve:start */
    property int curSectionId: display.id
    /* beautify preserve:end */
      sourceComponent: switch (display.classtype) {
        case "ImageSection": {
          return imageDelegate
        }
      }
    }

  }
}