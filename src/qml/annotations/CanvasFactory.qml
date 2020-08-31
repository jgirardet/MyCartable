import QtQuick 2.15
import "qrc:/js/drawcanvas.mjs" as DrawCanvas

Canvas {
    id: canvas

    property var mouse
    property bool painting: false
    property bool useDefaultTool: false
    property string tool: uiManager.annotationDessinCurrentTool
    property real lineWidth: uiManager.annotationDessinCurrentLineWidth
    property color strokeStyle: uiManager.annotationDessinCurrentStrokeStyle
    property color fillStyle: "transparent"
    property real startX
    property real startY
    property real endX
    property real endY
    property var arrowPoints
    property bool wasFillRect: false

    function startDraw(fallback) {
        useDefaultTool = fallback ? true : false;
        startX = mouse.mouseX;
        startY = mouse.mouseY;
        canvas.opacity = 1;
        painting = true;
    }

    function endDraw(sectionId) {
        painting = false;
        if (tool == "arrow")
            endDrawArrow(sectionId);
        else
            endDrawAll(sectionId);
        useDefaultTool = false;
        visible = false;
        fillStyle = "transparent";
        if (wasFillRect) {
            uiManager.annotationDessinCurrentTool = "fillrect";
            wasFillRect = false;
        }
    }

    function endDrawArrow(sectionId) {
        var mx = mouse.mouseX;
        var my = mouse.mouseY;
        var minX = Math.min(startX, mx, arrowPoints[0].x, arrowPoints[1].x, arrowPoints[2].x);
        var maxX = Math.max(startX, mx, arrowPoints[0].x, arrowPoints[1].x, arrowPoints[2].x);
        var minY = Math.min(startY, my, arrowPoints[0].y, arrowPoints[1].y, arrowPoints[2].y);
        var maxY = Math.max(startY, my, arrowPoints[0].y, arrowPoints[1].y, arrowPoints[2].y);
        var new_width = maxX - minX + lineWidth;
        var new_height = maxY - minY + lineWidth;
        arrowPoints = [];
        var lw = lineWidth / 2;
        var newX = startX <= mx ? startX - lw : mx - lineWidth * 5;
        var newY = startY <= my ? startY - lw : my - lineWidth * 5;
        var nStartX = startX - newX;
        var nStartY = startY - newY;
        var nEndX = mx - newX;
        var nEndY = my - newY;
        parent.model.newDessin({
            "x": newX / width,
            "y": newY / height,
            "startX": nStartX / new_width,
            "startY": nStartY / new_height,
            "endX": nEndX / new_width,
            "endY": nEndY / new_height,
            "width": new_width / width,
            "height": new_height / height,
            "tool": tool,
            "lineWidth": lineWidth,
            "strokeStyle": strokeStyle,
            "fillStyle": fillStyle,
            "opacity": opacity
        });
    }

    function endDrawAll(sectionId) {
        var lw = lineWidth / 2;
        var mx = mouse.mouseX;
        var my = mouse.mouseY;
        if (Qt.point(startX, startY) == Qt.point(mx, my))
            return ;

        // not tested
        var newX = startX <= mx ? startX - lw : mx - lw;
        var newY = startY <= my ? startY - lw : my - lw;
        var new_width = Math.abs(startX - mx) + lineWidth;
        var new_height = Math.abs(startY - my) + lineWidth;
        var nStartX = startX - newX;
        var nStartY = startY - newY;
        var nEndX = mx - newX;
        var nEndY = my - newY;
        parent.model.newDessin({
            "x": newX / width,
            "y": newY / height,
            "startX": nStartX / new_width,
            "startY": nStartY / new_height,
            "endX": nEndX / new_width,
            "endY": nEndY / new_height,
            "width": new_width / width,
            "height": new_height / height,
            "tool": tool,
            "lineWidth": lineWidth,
            "strokeStyle": strokeStyle,
            "fillStyle": fillStyle,
            "opacity": opacity
        });
    }

    visible: false
    onPaint: {
        // not tested
        if (startX == mouse.mouseX || startY == mouse.mouseY)
            return ;

        var ctx = canvas.getContext("2d");
        if (!painting)
            return ;

        if (useDefaultTool)
            uiManager.annotationDessinCurrentTool = "fillrect";

        if (tool == "fillrect") {
            canvas.opacity = 0.2;
            wasFillRect = true;
            uiManager.annotationDessinCurrentTool = "rect";
            canvas.fillStyle = canvas.strokeStyle;
        }
        ctx.lineWidth = canvas.lineWidth;
        ctx.fillStyle = canvas.fillStyle;
        ctx.strokeStyle = canvas.strokeStyle;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        visible = true;
        var tool_to_use = tool;
        arrowPoints = DrawCanvas.drawCanvas(ctx, tool, startX, startY, mouse.mouseX, mouse.mouseY);
    }
}
