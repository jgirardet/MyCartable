import QtQuick 2.14

Canvas {
  id: canvas

  /* beautify preserve:start */
  property var mouse
  property bool painting: false
  property string tool: "rect"
  property real lineWidth: 5
  property color fillStyle: "red"
  property color strokeStyle: "blue"
  property real startX
  property real startY
  property real endX
  property real endY
  visible: painting
  /* beautify preserve:end */

  onPaint: {
    if (startX == mouse.mouseX || startY == mouse.mouseY) {
      return
    }
    var ctx = canvas.getContext('2d')
    ctx.lineWidth = canvas.lineWidth
    ctx.fillStyle = canvas.fillStyle
    ctx.strokeStyle = canvas.strokeStyle
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    if (!painting) {
      return
    } else if (tool == "trait") {
      ctx.beginPath()
      ctx.moveTo(startX, startY)
      ctx.lineTo(mouse.mouseX, mouse.mouseY)
      ctx.stroke()
    } else if (tool == "rect") {
      print(startX, startY, mouse.mouseX, mouse.mouseY, mouse.mouseX - startX, mouse.mouseY - startY)
      ctx.strokeRect(startX, startY, mouse.mouseX - startX, mouse.mouseY - startY)
    } else if (tool == "fillrect") {
      print("fillrect")
      canvas.opacity = 0.2
      ctx.fillRect(startX, startY, mouse.mouseX - startX, mouse.mouseY - startY)
    } else if (tool == "ellipse") {
      print("ellipse")
      ctx.beginPath()
      ctx.ellipse(startX, startY, mouse.mouseX - startX, mouse.mouseY - startY)
      ctx.stroke()
    }
  }

  function startDraw() {
    painting = true
    startX = mouse.mouseX
    startY = mouse.mouseY
    print(startX, startY)
  }

  function endDraw(sectionId) {
    painting = false

    var lw = lineWidth / 2
    var mx = mouse.mouseX
    var my = mouse.mouseY
    var newX = startX <= mx ? startX - lw : mx - lw
    var newY = startY <= my ? startY - lw : my - lw

    if (Qt.point(startX, startY) == Qt.point(mx, my)) {
      return
    }
    var new_width = Math.abs(startX - mx) + lineWidth
    var new_height = Math.abs(startY - my) + lineWidth
    parent.model.newDessin(sectionId, {

      "x": newX / width,
      "y": newY / height,
      //      "startX": startX,
      //      "startY": startY,
      //      "endX": endX,
      //      "endY": endY,
      "width": new_width / width,
      "height": new_height / height,
      "tool": tool,
      "lineWidth": lineWidth,
      "strokeStyle": strokeStyle,
      "fillStyle": fillStyle,
    })
    canvas.context.clearRect(0, 0, canvas.width, canvas.height)

  }
}