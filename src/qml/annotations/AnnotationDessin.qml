import QtQuick 2.14

Canvas {
    //    }
    //      canvas.save("tests/qml_tests/assets/trait.png") // pour tests
    //      canvas.save("tests/qml_tests/assets/rect.png") // pour tests
    //      canvas.save("tests/qml_tests/assets/fillrect.png") // pour tests
    //      canvas.save("tests/qml_tests/assets/ellipse.png") // pour tests

    id: canvas

    // beautify preserve:start
    property var referent
    property var menu: uiManager.menuFlottantAnnotationDessin
    property color strokeStyle: annot.fgColor
    property color fillStyle: annot.bgColor
    property real lineWidth: annot.pointSize

    function checkPointIsNotDraw(mx, my) {
        var ctx = canvas.getContext("2d");
        mx = ~~mx;
        my = ~~my;
        var vWidth = ~~width;
        var vHeight = ~~height;
        var dd = ctx.getImageData(0, 0, vWidth, height).data;
        var debut = (vWidth * my + mx) * 4;
        var couleur = Qt.rgba(dd[debut], dd[debut + 1], dd[debut + 2], dd[debut + 3]);
        return Qt.colorEqual("#00000000", couleur);
    }

    width: annot.width * referent.implicitWidth
    height: annot.height * referent.implicitHeight
    // beautify preserve:end
    Component.onCompleted: {
        canvas.requestPaint();
    }
    onStrokeStyleChanged: requestPaint()
    onFillStyleChanged: requestPaint()
    onLineWidthChanged: requestPaint()
    onPaint: {
        // init variables
        var lw = lineWidth / 2;
        var startX = annot.startX * width;
        var startY = annot.startY * height;
        var endX = annot.endX * width;
        var endY = annot.endY * height;
        if (annot.tool == "fillrect")
            canvas.opacity = 0.2;

        var ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.lineWidth = lineWidth;
        ctx.fillStyle = fillStyle;
        ctx.strokeStyle = strokeStyle;
        // draw
        if (annot.tool == "trait") {
            ctx.beginPath();
            ctx.moveTo(startX, startY);
            ctx.lineTo(endX, endY);
            ctx.stroke();
        } else if (annot.tool == "rect") {
            ctx.strokeRect(startX, startY, endX - startX, endY - startY);
        } else if (annot.tool == "fillrect") {
            ctx.fillRect(startX, startY, endX - startX, endY - startY);
        } else if (annot.tool == "ellipse") {
            ctx.beginPath();
            ctx.ellipse(startX, startY, endX - startX, endY - startY);
            ctx.stroke();
        }
    }
}
