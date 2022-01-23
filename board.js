class Board
{
  constructor()
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
      }
    }
  }

  click(posX, posY)
  {
    let col = Math.floor(map(posX, -(this.board_width / 2), (this.board_width / 2), 0, 8));
    let row = Math.floor(map(posY, -(this.board_width / 2), (this.board_width / 2), 0, 8));
    if(row >=0 && row < 8 && col >= 0 && col < 8)
    {
      print(this.colMap[col] + this.rowMap[row]);
    }
  }
}