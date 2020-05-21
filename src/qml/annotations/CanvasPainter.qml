import QtQuick 2.14

Canvas {
  id: canvas
  /* beautify preserve:start */
  property var referent
  width: annot.width*referent.implicitWidth
  height: annot.height*referent.implicitHeight
  /* beautify preserve:end */

  Component.onCompleted: {
    print(JSON.stringify(annot))
    print(referent.implicitWidth, referent.implicitHeight)
    print("wh,h", x, y, width, height)
    canvas.requestPaint()
  }
  onPaint: {
    // init variables
    var lw = annot.pointSize / 2

    var startX = lw
    var startY = lw
    var endX = width - lw
    var endY = height - lw

    if (annot.tool == "fillrect") {
      canvas.opacity = 0.2
    }
    var ctx = canvas.getContext('2d')
    ctx.lineWidth = annot.pointSize
    ctx.fillStyle = annot.bgColor
    ctx.strokeStyle = annot.fgColor
    //    ctx.clearRect(0, 0, annot.width, annot.height)
    print("patin", ctx.fillStyle)

    // draw
    if (annot.tool == "trait") {
      ctx.beginPath()
      ctx.moveTo(startX, startY)
      ctx.lineTo(endX, endY)
      ctx.stroke()
    } else if (annot.tool == "rect") {
      ctx.strokeRect(startX, startY, endX - startX, endY - startY)
    } else if (annot.tool == "fillrect") {
      print("fill rect")
      ctx.fillRect(startX, startY, endX - startX, endY - startY)
    } else if (annot.tool == "ellipse") {
      ctx.beginPath()
      ctx.ellipse(startX, startY, endX - startX, endY - startY)
      ctx.stroke()
    }
  }

}