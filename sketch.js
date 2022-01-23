let cx, cy;
let board;

function setup()
{
  createCanvas(1760, 920);

  cx = width / 2;
  cy = height / 2;

  board = new Board();
}

function draw()
{
  translate(cx, cy);
  board.draw();
  noLoop();
}

function mouseClicked()
{
  board.click(mouseX - cx, mouseY - cy);
}