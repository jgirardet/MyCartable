import QtQuick 2.14

Canvas {
  anchors.fill: parent
  id: canvas
  /* beautify preserve:start */
  property int startX
  property int startY
  property int endX: 0
  property int endY: 0
  property var mouse
  property bool painting: false
  property string tool: "trait"
  /* beautify preserve:end */

  onPaint: {
    var ctx = canvas.getContext('2d')
    ctx.lineWidth = 5
    ctx.fillStyle = Qt.rgba(1, 0, 0, 1)
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    if (!painting) {
      return
    } else if (tool == "trait") {
      ctx.beginPath()
      ctx.moveTo(startX, startY)
      ctx.lineTo(mouse.mouseX, mouse.mouseY)
      ctx.stroke()
      print(mouse.mouseX, mouse.mouseY)
    }
  }

  function startDraw() {
    painting = true
    startX = mouse.mouseX
    startY = mouse.mouseY
    print(startX, startY)
  }

  function endDraw() {
    painting = false
    endX = mouse.mouseX
    endY = mouse.mouseY
    print(startX, startY, endX, endY, tool, canvas.toDataURL())
  }
}