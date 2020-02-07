import QtQuick 2.12
import QtQuick.Controls 2.12

ListView {
  id: lv
  spacing: 10
  clip: true

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
      /* beautify preserve:start */
    property int curSectionId: display.id
    /* beautify preserve:end */
      sourceComponent: switch (display.classtype) {
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