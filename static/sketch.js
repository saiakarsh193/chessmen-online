let cx, cy;
let board;
let pieces_img;

function preload()
{
  let imp = "/static/pieces/";
  pieces_img = [loadImage(imp + "P.png"), loadImage(imp + "R.png"), loadImage(imp + "N.png"), loadImage(imp + "B.png"), loadImage(imp + "Q.png"), loadImage(imp + "K.png"), loadImage(imp + "p.png"), loadImage(imp + "r.png"), loadImage(imp + "n.png"), loadImage(imp + "b.png"), loadImage(imp + "q.png"), loadImage(imp + "k.png")];
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