let cx, cy;
let board;
let pieces_img;
let img_sheet;

function preload()
{
  img_sheet = loadImage("/static/piece_sheet.png");
}

function setup()
{
  createCanvas(1760, 920);

  cx = width / 2;
  cy = height / 2;

  pieces_img = [
    img_sheet.get(  0, 312, 119, 141), // P
    img_sheet.get(  0, 450, 119, 141), // R
    img_sheet.get(149, 450, 119, 141), // N
    img_sheet.get(297, 450, 119, 141), // B
    img_sheet.get(452, 450, 119, 141), // Q
    img_sheet.get(601, 450, 119, 141), // K
    img_sheet.get(  0, 160, 119, 141), // p
    img_sheet.get(  0,   0, 119, 141), // r
    img_sheet.get(149,   0, 119, 141), // n
    img_sheet.get(297,   0, 119, 141), // b
    img_sheet.get(452,   0, 119, 141), // q
    img_sheet.get(601,   0, 119, 141)  // k
  ];

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