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


            var new_x = sx <= ex ? ex -arrowSize/2 : ex + arrowSize/2
            var new_y = alpha*new_x + beta
//             drawArrowhead(ctx, Qt.point(sx, sy),Qt.point(new_x, new_y), arrowSize)
            return  drawArrowhead(ctx, Qt.point(sx, sy),Qt.point(ex, ey), arrowSize)
//             var points = drawArrowhead(ctx, Qt.point(new_x, new_y),Qt.point(ex, ey), arrowSize)
        }

function drawArrowhead(context, from, to, radius) {
    // thanks to https://gist.github.com/jwir3/d797037d2e1bf78a9b04838d73436197
//     var x_center = to.x-context.lineWidth;
//     var x_center = to.x-context.lineWidth;
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
    print(point1, point2, point3)
    context.fill();
    context.closePath();

    return [point1, point2,point3]

}