  // Moving box 2 box intercepts

var objBox = createBox(0, 0, 0, 0);   // the moving box
var objLine = createLine(0, 0, 0, 0); // the line representing the box movement
var boxes = [];                       // array of boxes to check against


//Find closest intercept to start of line
function findIntercepts(B, L) {
    lineAddSlopes(L);   // get slopes and extras for line (one off calculation)
                        // for each obstacles check for intercept;
    for (var i = 0; i < boxes.length; i++) {
        intercept(B, L, boxes[i]);
    }
    // Line will hold the intercept pos as minX, minY, the normals of the side hit in nx,ny
    // and the dist from the line start squared
}


function lineAddSlopes(l) {           // adds the slopes of the lie for x,y and length as dist
    var dx = l.x2 - l.x1;             // vector from start to end of line
    var dy = l.y2 - l.y1;
    var dist = dx * dx + dy * dy;
    l.dx = dx / dy;                   // slope of line in terms of y to find x
    l.dy = dy / dx;                   // slope of line in terms of x to find y
    l.dist = dist;
   l.minX = dx;                      // the 2D intercept point.
    l.minY = dy;
    l.nx = 0;                         // the face normal of the intercept point
    l.ny = 0;
}


function intercept(b1, l, b2) { // find the closest intercept, if any, of b1 (box1) moving along l (line1)
                                // with b2. l.minX,l.minY will hold the position of the intercept point
                                // l.dist will hold the distance squared of the point from the line start
    var check = false;
    var lr = l.x1 < l.x2; // lf for (l)eft to (r)ight is true is line moves from left to right.
    var tb = l.y1 < l.y2; // tb for (t)op to (b)ottom is true is line moves from top to bottom
    var w2 = b1.w / 2;    // half width and height of box 1
    var h2 = b1.h / 2;

    // get extended sides of  box2. They are extended by half box1 width, height on all sides
    var right = b2.x + b2.w + w2;
    var left = b2.x - w2;
    var top = b2.y - h2;
    var bottom = b2.y + b2.h + h2;

    // check if box2 is inside the bounding box of the line
    if (lr) {                                      // if line from left to right
        check = (l.x1 < right && l.x2 > left);     // right hand side expression evaluates to boolean
    } else {
        check = (l.x2 < right && l.x1 > left);     // right hand side expression evaluates to boolean
    }
    if (check) {
        if (tb) {                                  // if line from top to bottom
            check = (l.y1 < bottom && l.y2 > top); // right hand side expression evaluates to boolean
        } else {
            check = (l.y2 < bottom && l.y1 > top); // right hand side expression evaluates to boolean
        }
    }
    if (check) {                                   // check is true if box2 needs to be checked
        ctx.strokeStyle = "blue";                  // draw box2's extened outline
        ctx.globalAlpha = 0.4;
        drawBox(b2, w2, h2);
        ctx.globalAlpha = 1;                       // set up for marking the intercept points if any
        ctx.fillStyle = "yellow";

        // Next check the horizontal and vertical lines around box2 that are closest to the line start
        // Use the slopes to calculate the x and y intercept points

        var lrSide = lr ? left : right;                               // get the closest top bottom side
        var tbSide = tb ? top : bottom;                               // get the closest top bottom side


        var distX = lrSide - l.x1;                                    // find x distance to closest side of box
        var distY = tbSide - l.y1;                                    // find y distance to closest side of box

        var posX = l.x1 + distY * l.dx;                               // use x slope to find X intercept of top or bottom
        var posY = l.y1 + distX * l.dy;                               // use y slope to find Y intercept of left or right
        if (posX >= left && posX <= right) {                          // is posX on the box perimeter?
            drawMark(posX, tbSide, 8);                                // mark the point
            var dist = distY * distY + (posX - l.x1) * (posX - l.x1); // get the distance to the intercept squared
            if (dist < l.dist) {                                      // is this intercept closer than any previous found intercepts?
                l.dist = dist;                                        // save the distance
                l.minX = posX - l.x1;                                 // and the x,y coordinate of intercept
                l.minY = tbSide - l.y1;
                l.nx = 0;                                             // get the normal of the line hit
                l.ny = tb ? -1 : 1;
            }
        }
        if (posY >= top && posY <= bottom) {                          // is posY on the box perimeter
            drawMark(lrSide, posY, 8);                                // mark the point
            var dist = distX * distX + (posY - l.y1) * (posY - l.y1); // get the distance to the intercept squared
            if (dist < l.dist) {                                      // is this intercept closer than any previous found intercepts?
                l.dist = dist;                                        // save the distance
                l.minX = lrSide - l.x1;                               // and the x,y coordinate of intercept
                l.minY = posY - l.y1;
                l.nx = lr ? -1 : 1;                                   // get the normal of the line hit
                l.ny = 0;
            }
        }
   }
 }