import QtQuick 2.15
import "qrc:/js/drawcanvas.mjs" as DrawCanvas
import "qrc:/qml/menu"

Canvas {
    //      canvas.save("tests/qml/assets/trait.png") // pour tests
    //      canvas.save("tests/qml/assets/rect.png") // pour tests
    //      canvas.save("tests/qml/assets/fillrect.png") // pour tests
    //      canvas.save("tests/qml/assets/ellipse.png") // pour tests

    id: canvas

    property var referent
    property alias menu: menuFlottantAnnotationDessin
    property QtObject annot
    property color strokeStyle: annot.fgColor
    property color fillStyle: annot.bgColor
    property real lineWidth: annot.pointSize
    property string tool: annot.tool
    property int modelIndex: index // à priori pas utilisé ici mais on garde pour l'interface

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

    opacity: annot.weight / 10
    width: annot.width * referent.implicitWidth
    height: annot.height * referent.implicitHeight
    Component.onCompleted: {
        canvas.requestPaint();
    }
    onStrokeStyleChanged: {
        requestPaint();
    }
    onFillStyleChanged: requestPaint()
    onLineWidthChanged: requestPaint()
    onPaint: {
        var ctx = canvas.getContext("2d");
        ctx.lineWidth = lineWidth;
        ctx.fillStyle = fillStyle;
        ctx.strokeStyle = strokeStyle;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        if (tool == "point") {
            DrawCanvas.drawPoints(ctx, annot.points, lineWidth / 2, width, height);
        } else {
            var lw = lineWidth / 2;
            var startX = annot.startX * width;
            var startY = annot.startY * height;
            var endX = annot.endX * width;
            var endY = annot.endY * height;
            DrawCanvas.drawCanvas(ctx, tool, startX, startY, endX, endY);
        }
    }

    MenuFlottantAnnotationDessin {
        id: menuFlottantAnnotationDessin
    }

}
