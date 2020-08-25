import QtQuick 2.14
import "qrc:/qml/menu"

Item {
    property var menuTarget
    property var menuFlottantAnnotationText
    property var menuFlottantAnnotationDessin
    property var menuFlottantText
    property var menuFlottantTableau
    property var menuFlottantImage
    property int annotationCurrentTextSizeFactor: 15
    property string annotationDessinCurrentTool: "fillrect"
    property real annotationDessinCurrentLineWidth: 3
    property color annotationDessinCurrentStrokeStyle: "black"
    property string annotationCurrentTool: "text"

    menuFlottantAnnotationText: MenuFlottantAnnotationText {
    }

    menuFlottantAnnotationDessin: MenuFlottantAnnotationDessin {
    }

    menuFlottantText: MenuFlottantText {
    }

    menuFlottantTableau: MenuFlottantTableau {
    }

    menuFlottantImage: MenuFlottantImage {
    }

}
