import QtQuick 2.14

Canvas {
  id: canvas

  /* beautify preserve:start */
  property var mouse
  property bool painting: false
  property bool useDefaultTool: false
  property string tool: uiManager.annotationDessinCurrentTool
  property real lineWidth: uiManager.annotationDessinCurrentLineWidth
  property color fillStyle: uiManager.annotationDessinCurrentStrokeStyle
  property color strokeStyle: uiManager.annotationDessinCurrentStrokeStyle
  property real startX
  property real startY
  property real endX
  property real endY
  visible: false
  /* beautify preserve:end */

  onPaint: {
    // not tested
    if (startX == mouse.mouseX || startY == mouse.mouseY) {
      return
    }
    var ctx = canvas.getContext('2d')
    ctx.lineWidth = canvas.lineWidth
    ctx.fillStyle = canvas.fillStyle
    ctx.strokeStyle = canvas.strokeStyle
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    visible = true
    if (!painting) {
      return
    } else if (useDefaultTool) {
      canvas.opacity = 0.2
      ctx.fillRect(startX, startY, mouse.mouseX - startX, mouse.mouseY - startY)
    } else if (tool == "trait") {
      ctx.beginPath()
      ctx.moveTo(startX, startY)
      ctx.lineTo(mouse.mouseX, mouse.mouseY)
      ctx.stroke()
    } else if (tool == "rect") {
      ctx.strokeRect(startX, startY, mouse.mouseX - startX, mouse.mouseY - startY)
    } else if (tool == "fillrect") {
      canvas.opacity = 0.2
      ctx.fillRect(startX, startY, mouse.mouseX - startX, mouse.mouseY - startY)
    } else if (tool == "ellipse") {
      ctx.beginPath()
      ctx.ellipse(startX, startY, mouse.mouseX - startX, mouse.mouseY - startY)
      ctx.stroke()
    }
  }

  function startDraw(fallback) {
    useDefaultTool = fallback ? true : false
    startX = mouse.mouseX
    startY = mouse.mouseY
    canvas.opacity = 1
    painting = true
  }

  function endDraw(sectionId) {
    painting = false
    var lw = lineWidth / 2
    var mx = mouse.mouseX
    var my = mouse.mouseY
    if (Qt.point(startX, startY) == Qt.point(mx, my)) {
      return
    }
    // not tested
    var newX = startX <= mx ? startX - lw : mx - lw
    var newY = startY <= my ? startY - lw : my - lw
    var new_width = Math.abs(startX - mx) + lineWidth
    var new_height = Math.abs(startY - my) + lineWidth
    var nStartX = startX - newX
    var nStartY = startY - newY
    var nEndX = mx - newX
    var nEndY = my - newY

    parent.model.newDessin(sectionId, {
      "x": newX / width,
      "y": newY / height,
      "startX": nStartX / new_width,
      "startY": nStartY / new_height,
      "endX": nEndX / new_width,
      "endY": nEndY / new_height,
      "width": new_width / width,
      "height": new_height / height,
      "tool": useDefaultTool ? "fillrect" : tool,
      "lineWidth": lineWidth,
      "strokeStyle": strokeStyle,
      "fillStyle": fillStyle,
    })
    useDefaultTool = false
    visible = false
  }
}