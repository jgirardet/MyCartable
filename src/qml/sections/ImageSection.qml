//import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/annotations"
import "qrc:/qml/menu"

Image {
    id: root

    required property Item sectionItem
    required property QtObject section
    property var model
    property MouseArea mousearea: mousearea
    property var currentAnnotation
    property Item annotations: repeater
    property alias menu: menuFlottantImage

    signal loaded(int idx)

    function reloadImage() {
        // not tested
        sourceClipRect = root.childrenRect;
        sourceClipRect = undefined;
    }

    function setStyleFromMenu(datas) {
        if ("style" in datas) {
            if ("pointSize" in datas["style"])
                section.annotationDessinCurrentLineWidth = datas["style"]["pointSize"];

            if ("fgColor" in datas["style"])
                section.annotationDessinCurrentStrokeStyle = datas["style"]["fgColor"];

            if ("tool" in datas["style"]) {
                var newTool = datas["style"]["tool"];
                section.annotationCurrentTool = newTool;
                if (newTool == "text")
                    section.annotationDessinCurrentTool = "fillrect";
                else
                    section.annotationDessinCurrentTool = newTool;
                section.setImageSectionCursor(mousearea, section.annotationCurrentTool, section.annotationDessinCurrentStrokeStyle);
            }
        }
    }

    function startDraw(fallback) {
        if (section.annotationCurrentTool == "point")
            mainlevee.startDraw();
        else
            canvas.startDraw(fallback);
    }

    function addAnnotationText(mouse) {
        model.addAnnotation("AnnotationText", {
            "x": mouse.x,
            "y": mouse.y,
            "width": width,
            "height": height
        });
    }

    asynchronous: true
    fillMode: Image.PreserveAspectCrop
    sourceSize.width: sectionItem ? sectionItem.width : 0
    cache: false
    Component.onCompleted: {
        root.source = section.url;

    }
    Connections {
      target: section
      function onCommandDone() {
        root.reloadImage()
      }
    }
    model: section.model

    MenuFlottantImage {
        id: menuFlottantImage
    }

    MouseArea {
        id: mousearea

        objectName: "mousearea"
        anchors.fill: root
        preventStealing: true
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        hoverEnabled: true
        onEntered: section.setImageSectionCursor(mousearea, section.annotationCurrentTool, section.annotationDessinCurrentStrokeStyle)
        onPressed: {
            if (pressedButtons === Qt.RightButton) {
                if (mouse.modifiers == Qt.ControlModifier)
                    root.startDraw(true);
                else
                    menuFlottantImage.ouvre(root);
            } else if (pressedButtons === Qt.LeftButton) {
                if (mouse.modifiers == Qt.ControlModifier) {
                    root.addAnnotationText(mouse);
                } else if (section.annotationCurrentTool == "text") {
                    root.addAnnotationText(mouse);
                } else if (section.annotationCurrentTool == "floodfill") {
                    let fillColor = section.annotationDessinCurrentStrokeStyle;
                    let point = Qt.point(mouse.x / width, mouse.y / height);
                    section.floodFill(fillColor, point);
                } else {
                    root.startDraw();
                }
                mouse.accepted = true;
            }
        }
        onReleased: {
            if (canvas.painting)
                canvas.endDraw(section.id);
            else if (mainlevee.painting)
                mainlevee.endDraw();
        }
        onPositionChanged: {
            if (pressed) {
                if (canvas.painting)
                    canvas.requestPaint();
                else if (mainlevee.painting)
                    mainlevee.requestPaint();
            }
        }
    }

    Repeater {
        id: repeater

        objectName: "repeater"
        anchors.fill: root
        model: root.status == Image.Ready ? root.model : 0
        onItemAdded: {
            mainlevee.visible = false;
            canvas.visible = false;
        }

        delegate: BaseAnnotation {
            id: repdelegate

            annot: annotation
            referent: root
            section: root.section
        }

    }

    CanvasFactory {
        id: canvas

        objectName: "canvasFactory"
        mouse: mousearea
        anchors.fill: root
        section: root.section
    }

    MainLevee {
        id: mainlevee

        section: root.section
        mouse: mousearea
        anchors.fill: root
        visible: false
    }

}
