let cx, cy;
let board;
let pieces_img;

function preload()
{
  pieces_img = [loadImage("./pieces/P.png"), loadImage("./pieces/R.png"), loadImage("./pieces/N.png"), loadImage("./pieces/B.png"), loadImage("./pieces/Q.png"), loadImage("./pieces/K.png"), loadImage("./pieces/p.png"), loadImage("./pieces/r.png"), loadImage("./pieces/n.png"), loadImage("./pieces/b.png"), loadImage("./pieces/q.png"), loadImage("./pieces/k.png")];
}

function setup()
{
  createCanvas(1760, 920);

  cx = width / 2;
  cy = height / 2;

  board = new Board(pieces_img);
}

function draw()
{
  translate(cx, cy);
  board.draw();
}

function mouseClicked()
{
  board.click(mouseX - cx, mouseY - cy);
}