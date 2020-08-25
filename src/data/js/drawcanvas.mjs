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
    }
}