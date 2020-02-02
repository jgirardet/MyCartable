import QtQuick 2.12
import QtQuick.Controls 2.12
import Qt.labs.qmlmodels 1.0
ListView {
  id: lv
  spacing: 10
  clip: true

  Component {
    id: texteDelegate
    PageTexteDelegate {
      text: datas.content;width: lv.width
    }
  }

  Component {
    id: imageDelegate
    AnnotableImage {
      content: datas
      base: lv
    }
  }

  delegate: Component {
    Loader {
      /* beautify preserve:start */
    property var datas: display
    /* beautify preserve:end */
      sourceComponent: switch (display.type) {
        case "texte":
          return texteDelegate
        case "img":
          return imageDelegate
      }
    }
  }
}