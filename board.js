function FENtoBoard(fen)
{
  let sfen = fen.split(" ");
  let mfen = sfen[0].split("/");
  let board = [];
  for(let r = 0;r < 8;r ++)
  {
    board.push([]);
    for(let i = 0;i < mfen[r].length;i ++)
    {
      if(! isNaN(mfen[r][i]))
      {
        for(let j = 0;j < Number(mfen[r][i]);j ++)
          board[r].push(" ")
      }
      else
        board[r].push(mfen[r][i]);
    }
  }
  return board;
}

function BoardToFEN(board)
{
  let fen = "";
  let ctr = 0;
  for(let r = 0;r < 8;r ++)
  {
    for(let c = 0;c < 8;c ++)
    {
      if(board[r][c] == " ")
        ctr += 1;
      if(board[r][c] != " " || c == 7)
      {
        if(ctr > 0)
        {
          fen += ctr;
          ctr = 0;
        }
        if(board[r][c] != " ")
          fen += board[r][c];
      }
    }
    if(r != 7)
      fen += "/";
  }
  return fen;
}

class Board
{
  constructor(pieces_img)
  {
    this.board_width = 800;
    this.cell_width = this.board_width / 8;
    this.text_cell_buff = 5;
    this.text_size = 24;
    this.color_green = color(119, 150, 87);
    this.color_white = color(238, 239, 211);
    this.color_black = color(38, 36, 34);
    this.color_grey_dark = color(49, 46, 43);
    this.player = 'white';
    if(this.player == 'white')
    {
      this.rowMap = [8, 7, 6, 5, 4, 3, 2, 1];
      this.colMap = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
    }
    else
    {
      this.rowMap = [1, 2, 3, 4, 5, 6, 7, 8];
      this.colMap = ['h', 'g', 'f', 'e', 'd', 'c', 'b', 'a'];
    }
    this.pieces_img = pieces_img;
    this.pieces_scale = 0.8;
    this.pieces_offset = 8;
    this.pieces_img.forEach((img) => 
    {
      img.resize(this.cell_width * this.pieces_scale, this.cell_width * this.pieces_scale);
    });
    this.piecesMap = {"P": 0, "R": 1, "N": 2, "B": 3, "Q": 4, "K": 5, "p": 6, "r": 7, "n": 8, "b": 9, "q": 10, "k": 11};

    this.board = FENtoBoard("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR");
    this.active = "";
  }

  draw()
  {
    background(this.color_black);
    noStroke();
    textSize(this.text_size);
    textFont('Sans-serif');
    for(let row = 0;row < 8;row ++)
    {
      for(let col = 0;col < 8;col ++)
      {
        // cells
        if((row + col) % 2)
          fill(this.color_green);
        else
          fill(this.color_white);
        let cx = map(col, 0, 8, -(this.board_width / 2), (this.board_width / 2));
        let cy = map(row, 0, 8, -(this.board_width / 2), (this.board_width / 2));
        if(row == 0 && col == 0)
          square(cx, cy, this.cell_width, 10, 0, 0, 0);
        else if(row == 0 && col == 7)
          square(cx, cy, this.cell_width, 0, 10, 0, 0);
        else if(row == 7 && col == 7)
          square(cx, cy, this.cell_width, 0, 0, 10, 0);
        else if(row == 7 && col == 0)
          square(cx, cy, this.cell_width, 0, 0, 0, 10);
        else
          square(cx, cy, this.cell_width);
        // letters
        if((row + col) % 2)
          fill(this.color_white);
        else
          fill(this.color_green);
        if(row == 7)
        {
          textAlign(RIGHT, BOTTOM);
          text(this.colMap[col], cx + this.cell_width - this.text_cell_buff, cy + this.cell_width - this.text_cell_buff);
        }
        if(col == 0)
        {
          textAlign(LEFT, TOP);
          text(this.rowMap[row], cx + this.text_cell_buff, cy + this.text_cell_buff);
        }
        // pieces
        if(this.board[row][col] != " ")
          image(this.pieces_img[this.piecesMap[this.board[row][col]]], cx + this.pieces_offset, cy + this.pieces_offset);
      }
    };
  }

  click(posX, posY)
  {
    let col = Math.floor(map(posX, -(this.board_width / 2), (this.board_width / 2), 0, 8));
    let row = Math.floor(map(posY, -(this.board_width / 2), (this.board_width / 2), 0, 8));
    if(row >=0 && row < 8 && col >= 0 && col < 8)
    {
      if(this.active == "")
      {
        this.active = [row, col];
      }
      else
      {
        this.board[row][col] = this.board[this.active[0]][this.active[1]];
        this.board[this.active[0]][this.active[1]] = " ";
        this.active = "";
      }
    }
  }
}