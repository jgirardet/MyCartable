import QtQuick 2.15
import "qrc:/js/drawcanvas.mjs" as DrawCanvas

Canvas {
    id: canvas

    property var mouse
    property bool painting: false
    property QtObject section
    property real lineWidth: section.annotationDessinCurrentLineWidth
    property color strokeStyle: section.annotationDessinCurrentStrokeStyle
    property var points: []

    function startDraw(fallback) {
        points = [];
        canvas.opacity = 1;
        painting = true;
        points.push(Qt.point(mouse.mouseX / width, mouse.mouseY / height));
    }

    function endDraw() {
        painting = false;
        saveDraw();
    }

    function saveDraw() {
        let res = {
            "x": 0,
            "y": 0,
            "startX": 0,
            "startY": 0,
            "endX": 1,
            "endY": 1,
            "width": 1,
            "height": 1,
            "tool": "point",
            "points": JSON.stringify(points),
            "lineWidth": lineWidth,
            "strokeStyle": strokeStyle,
            "fillStyle": strokeStyle,
            "opacity": opacity
        };
        parent.model.addAnnotation("AnnotationDessin", res);
    }

    visible: false
    onPaint: {
        var ctx = canvas.getContext("2d");
        if (!painting)
            return ;

        ctx.lineWidth = canvas.lineWidth;
        ctx.fillStyle = canvas.strokeStyle;
        ctx.strokeStyle = canvas.strokeStyle;
        visible = true;
        let lastPoint = Qt.point(points[points.length - 1].x * width, points[points.length - 1].y * height);
        let newPoint = Qt.point(mouse.mouseX, mouse.mouseY);
        DrawCanvas.drawBetweenPoints(ctx, lastPoint, newPoint);
        let ratioPoint = Qt.point(newPoint.x / width, newPoint.y / height);
        points.push(ratioPoint);
    }
}
