import QtQuick 2.14
import "qrc:/qml/menu"

Item {
    // beautify preserve:stop

    property var menuTarget
    property var menuFlottantAnnotationText

    menuFlottantAnnotationText: MenuFlottantAnnotationText {
    }

    property var menuFlottantText

    menuFlottantText: MenuFlottantText {
    }

    property var menuFlottantTableau

    menuFlottantTableau: MenuFlottantTableau {
    }

    property var menuFlottantImage

    menuFlottantImage: MenuFlottantImage {
    }

    property int annotationCurrentTextSizeFactor: 15
    property string annotationDessinCurrentTool: "fillrect"
    property real annotationDessinCurrentLineWidth: 3
    property color annotationDessinCurrentStrokeStyle: "black"
    property string annotationCurrentTool: "text"
}
