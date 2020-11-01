export function drawCanvas (ctx, tool, startX, startY, endX, endY) {
    if (tool == "trait") {
        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.lineTo(endX, endY);
        ctx.stroke();
    } else if (tool == "rect") {
        ctx.beginPath();
        ctx.rect(startX, startY, endX - startX, endY - startY);
        ctx.fill();
        ctx.stroke();
    } else if (tool == "ellipse") {
        ctx.beginPath();
        ctx.ellipse(startX, startY, endX - startX, endY - startY);
        ctx.fill();
        ctx.stroke();
    } else if (tool == "arrow") {
        return drawArrow(ctx, startX, startY, endX, endY)
    }
}

function drawArrow(ctx, sx, sy, ex, ey) {
            var arrowSize = ctx.lineWidth*3
            ctx.fillStyle = "black"
             ctx.beginPath()
            ctx.moveTo(sx, sy)
            ctx.lineTo(ex, ey)
            ctx.stroke()
            ctx.closePath()

            var alpha = (ey-sy)/(ex-sx)
            var beta = ey - alpha * ex


//             var new_x = sx <= ex ? ex -arrowSize/2 : ex + arrowSize/2
//             var new_y = alpha*new_x + beta
            return  drawArrowhead(ctx, Qt.point(sx, sy),Qt.point(ex, ey), arrowSize)
        }

function drawArrowhead(context, from, to, radius) {
    // thanks to https://gist.github.com/jwir3/d797037d2e1bf78a9b04838d73436197
    var x_center = to.x;
    var y_center = to.y;

    var angle;
    var x;
    var y;

    context.beginPath();

    angle = Math.atan2(to.y - from.y, to.x - from.x)
    x = radius * Math.cos(angle) + x_center;
    y = radius * Math.sin(angle) + y_center;
    var point1 = Qt.point(x,y)
    context.moveTo(x, y);

    angle += (1.0/3.0) * (2 * Math.PI)
    x = radius * Math.cos(angle) + x_center;
    y = radius * Math.sin(angle) + y_center;
    var point2 = Qt.point(x,y)
    context.lineTo(x, y);


    angle += (1.0/3.0) * (2 * Math.PI)
    x = radius *Math.cos(angle) + x_center;
    y = radius *Math.sin(angle) + y_center;
    var point3 = Qt.point(x,y)
    context.lineTo(x, y);
    context.fill();
    context.closePath();

    return [point1, point2,point3]

}


export function drawPoints(ctx, points, lineWidth, width, height) {
  let lastPoint = Qt.point(points[0].x*width, points[0].y*height)
  for (const po of points.slice(1,points.length)) {
        let newPoint = Qt.point(po.x*width, po.y*height);
        drawBetweenPoints(ctx, lastPoint, newPoint)
        lastPoint = newPoint;
    }
}

export function drawBetweenPoints(ctx, start, end) {
  let diff = ctx.lineWidth / 2;
  let baseLineWidth = ctx.lineWidth
  //draw line
  ctx.beginPath();
  ctx.moveTo(start.x, start.y);
  ctx.lineWidth = baseLineWidth * 2;
  ctx.lineTo(end.x, end.y);
  ctx.stroke();
  //draw ellipse
  ctx.beginPath();
  ctx.lineWidth = baseLineWidth;
  ctx.ellipse(end.x - diff, end.y - diff, ctx.lineWidth, ctx.lineWidth);
  ctx.fill();
  ctx.stroke();
}