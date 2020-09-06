import QtQuick 2.15
import QtQuick.Controls 2.15
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
    property bool buzyIndicator: false

    signal sendToast(string msg)

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
