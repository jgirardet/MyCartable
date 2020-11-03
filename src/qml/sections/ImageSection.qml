import MyCartable 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/annotations"
import "qrc:/qml/menu"

Image {
    //        Binding {
    //            target: root.model
    //            when: rot.model.modelReady
    //            property: "sectionId"
    //            value: root.sectionId
    //        }
    //        sectionId: root.sectionId ? root.sectionId : ""

    id: root

    property string sectionId
    property var sectionItem
    property var model
    property MouseArea mousearea: mousearea
    property var currentAnnotation
    property Item annotations: repeater

    function reloadImage() {
        // not tested
        //        print(implicitHeight);
        //        let oldheight = height;
        sourceClipRect = root.childrenRect;
        sourceClipRect = undefined;
    }

    function setStyleFromMenu(datas) {
        if ("style" in datas) {
            if ("pointSize" in datas["style"])
                uiManager.annotationDessinCurrentLineWidth = datas["style"]["pointSize"];

            if ("fgColor" in datas["style"])
                uiManager.annotationDessinCurrentStrokeStyle = datas["style"]["fgColor"];

            if ("tool" in datas["style"]) {
                var newTool = datas["style"]["tool"];
                uiManager.annotationCurrentTool = newTool;
                if (newTool == "text")
                    uiManager.annotationDessinCurrentTool = "fillrect";
                else
                    uiManager.annotationDessinCurrentTool = newTool;
                ddb.setImageSectionCursor(mousearea);
            }
        }
    }

    function startDraw(fallback) {
        if (uiManager.annotationCurrentTool == "point")
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
        var content = ddb.loadSection(sectionId);
        var path = content.path.toString();
        root.source = path.startsWith("file:///") || path.startsWith("qrc:") ? content.path : "file:///" + path;
    }

    MouseArea {
        //                cursorShape = Qt.ArrowCursor;
        //                cursorShape = Qt.ArrowCursor;

        id: mousearea

        objectName: "mousearea"
        anchors.fill: root
        preventStealing: true
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        hoverEnabled: true
        onEntered: ddb.setImageSectionCursor(mousearea)
        onPressed: {
            if (pressedButtons === Qt.RightButton) {
                if (mouse.modifiers == Qt.ControlModifier)
                    root.startDraw(true);
                else
                    uiManager.menuFlottantImage.ouvre(root);
            } else if (pressedButtons === Qt.LeftButton) {
                if (mouse.modifiers == Qt.ControlModifier) {
                    root.addAnnotationText(mouse);
                } else if (uiManager.annotationCurrentTool == "text") {
                    root.addAnnotationText(mouse);
                } else if (uiManager.annotationCurrentTool == "floodfill") {
                    let fillColor = uiManager.annotationDessinCurrentStrokeStyle;
                    let point = Qt.point(mouse.x / width, mouse.y / height);
                    let res = ddb.floodFill(root.sectionId, fillColor, point);
                    root.reloadImage();
                } else {
                    root.startDraw();
                }
                mouse.accepted = true;
            }
        }
        onReleased: {
            if (canvas.painting)
                canvas.endDraw(root.sectionId);
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

            referent: root
        }

    }

    CanvasFactory {
        id: canvas

        objectName: "canvasFactory"
        mouse: mousearea
        anchors.fill: root
    }

    MainLevee {
        id: mainlevee

        mouse: mousearea
        anchors.fill: root
        visible: false
    }

    model: AnnotationModel {
        dao: ddb
        dtb: c_dtb
        Component.onCompleted: sectionId = root.sectionId
    }

}
