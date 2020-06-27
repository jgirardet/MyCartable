import QtQuick 2.14
import "qrc:/qml/menu"

Item {
  /* beautify preserve:start */
      property var menuTarget
      property var menuFlottantAnnotationText: MenuFlottantAnnotationText {}
      property var menuFlottantText: MenuFlottantText {}
      property var menuFlottantTableau: MenuFlottantTableau {}
      property var menuFlottantImage: MenuFlottantImage {}
      property int annotationCurrentTextSizeFactor: 15
      property string annotationDessinCurrentTool: "fillrect"
      property real annotationDessinCurrentLineWidth: 3
      property color annotationDessinCurrentStrokeStyle: "black"
      property string annotationCurrentTool: "text"
      /* beautify preserve:stop */
}