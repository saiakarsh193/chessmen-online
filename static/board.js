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
    constructor(pieces_img, myuid)
    {
        this.board_width = 800;
        this.cell_width = this.board_width / 8;
        this.text_cell_buff = 5;
        this.text_size = 22;
        this.valid_circle_diam = 35;
        this.target_ring_width = 8;

        this.color_green = color(119, 150, 87);
        this.color_white = color(238, 239, 211);
        this.color_black = color(38, 36, 34);
        this.color_grey_dark = color(49, 46, 43);
        this.color_active_green = color(186,202,42);
        this.color_active_white = color(246,246,106);
        this.color_valid = color(100, 100, 100, 80);
        
        this.pieces_img = pieces_img;
        this.pieces_scale = 0.68;
        this.pieces_offset_x = 9;
        this.pieces_offset_y = 4;
        this.pieces_img.forEach((img) => 
        {
            img.resize(img.width * this.pieces_scale, img.height * this.pieces_scale);
        });
        this.piecesMap = {"P": 0, "R": 1, "N": 2, "B": 3, "Q": 4, "K": 5, "p": 6, "r": 7, "n": 8, "b": 9, "q": 10, "k": 11};

        this.active_cell = "";
        this.valid_cells = [];
        this.target_cells = [];

        this.myuid = myuid;
        this.start = false;
        this.rowMap = [8, 7, 6, 5, 4, 3, 2, 1];
        this.colMap = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
        this.flip_board = false;
        this.cfen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR";
        this.makeBoard();

        this.connect_time = millis();
        this.pgctr = 0;
    }

    makeBoard()
    {
        let tfen = this.cfen;
        if(this.flip_board)
            tfen = this.cfen.split("").reverse().join("");
        this.board = FENtoBoard(tfen);
    }

    assign(player)
    {
        this.player = player;
        if(this.player == 'black')
        {
            this.rowMap = [1, 2, 3, 4, 5, 6, 7, 8];
            this.colMap = ['h', 'g', 'f', 'e', 'd', 'c', 'b', 'a'];
            this.flip_board = true;
            this.makeBoard();
        }
        this.start = true;
    }

    draw()
    {
        if(millis() - this.connect_time > 200 && this.start)
        {
            this.connect_time = millis();
            this.update();
        }
        background(this.color_black);
        noStroke();
        textFont('Sans-serif');
        // user text
        textSize(this.text_size * 1.25);
        textAlign(LEFT, TOP);
        fill(this.color_green);
        text('you are: ' + this.myuid, -cx + 30, -(this.board_width / 2) + (textAscent() + 20) * 0);
        text('game status: ' + this.start, -cx + 30, -(this.board_width / 2) + (textAscent() + 20) * 1);
        if(this.start)
        {
            text('your color: ' + this.player, -cx + 30, -(this.board_width / 2) + (textAscent() + 20) * 2);
        }
        // board
        textSize(this.text_size);
        for(let row = 0;row < 8;row ++)
        {
            for(let col = 0;col < 8;col ++)
            {
                // cells
                if((row + col) % 2)
                    fill(this.color_green);
                else
                    fill(this.color_white);
                if(this.active_cell != "" && this.active_cell[0] == row && this.active_cell[1] == col)
                {
                    if((row + col) % 2)
                        fill(this.color_active_green);
                    else
                        fill(this.color_active_white);
                }
                let cx = map(col, 0, 8, -(this.board_width / 2), (this.board_width / 2));
                let cy = map(row, 0, 8, -(this.board_width / 2), (this.board_width / 2));
                if(row == 0 && col == 0)
                    square(cx, cy, this.cell_width, 5, 0, 0, 0);
                else if(row == 0 && col == 7)
                    square(cx, cy, this.cell_width, 0, 5, 0, 0);
                else if(row == 7 && col == 7)
                    square(cx, cy, this.cell_width, 0, 0, 5, 0);
                else if(row == 7 && col == 0)
                    square(cx, cy, this.cell_width, 0, 0, 0, 5);
                else
                    square(cx, cy, this.cell_width);
                // letters
                if((row + col) % 2)
                    fill(this.color_white);
                else
                    fill(this.color_green);
                if(this.active_cell != "" && this.active_cell[0] == row && this.active_cell[1] == col)
                {
                    if((row + col) % 2)
                        fill(this.color_active_white);
                    else
                        fill(this.color_active_green);
                }
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
                    image(this.pieces_img[this.piecesMap[this.board[row][col]]], cx + this.pieces_offset_x, cy + this.pieces_offset_y);
            }
        }
        // valid moves
        fill(this.color_valid);
        for(let i = 0;i < this.valid_cells.length;i ++)
        {
            let row = this.valid_cells[i][0];
            let col = this.valid_cells[i][1];
            let cx = map(col, 0, 8, -(this.board_width / 2), (this.board_width / 2));
            let cy = map(row, 0, 8, -(this.board_width / 2), (this.board_width / 2));
            circle(cx + (this.cell_width / 2), cy + (this.cell_width / 2), this.valid_circle_diam);
        }
        // target moves
        noFill();
        strokeWeight(this.target_ring_width);
        stroke(this.color_valid);
        for(let i = 0;i < this.target_cells.length;i ++)
        {
            let row = this.target_cells[i][0];
            let col = this.target_cells[i][1];
            let cx = map(col, 0, 8, -(this.board_width / 2), (this.board_width / 2));
            let cy = map(row, 0, 8, -(this.board_width / 2), (this.board_width / 2));
            circle(cx + (this.cell_width / 2), cy + (this.cell_width / 2), this.cell_width - this.target_ring_width);
        }
    }

    update()
    {
        postData('/ping', {'request': 'status'})
        .then(data =>
        {
            return data['response'];
        })
        .then(resp =>
        {
            if(resp == '<opponent turn>')
                this.pgctr = 0;
            else
            {
                if(this.pgctr == 0)
                {
                    postData('/ping', {'request': 'getfen'})
                    .then(data =>
                    {
                        return data['response'];
                    })
                    .then(resp =>
                    {
                        let srep = resp.substring(1, resp.length - 1).split(' :: ');
                        this.cfen = srep[1];
                        this.makeBoard();
                    });
                }
                this.pgctr = 1;
            }
        });
    }

    click(posX, posY)
    {
        let col = Math.floor(map(posX, -(this.board_width / 2), (this.board_width / 2), 0, 8));
        let row = Math.floor(map(posY, -(this.board_width / 2), (this.board_width / 2), 0, 8));
        if(row >=0 && row < 8 && col >= 0 && col < 8 && this.start)
        {
            // ask for status
            if(this.isValidMove(row, col))
            {
                this.board[row][col] = this.board[this.active_cell[0]][this.active_cell[1]];
                this.board[this.active_cell[0]][this.active_cell[1]] = " ";
                let tfen = BoardToFEN(this.board);
                if(this.flip_board)
                    tfen = tfen.split("").reverse().join("");
                this.cfen = tfen;
                // send this cfen
                postData('/ping', {'request': 'setfen : ' + this.cfen});
                this.valid_cells = [];
                this.target_cells = [];
                this.active_cell = "";
            }
            else
            {
                this.valid_cells = [];
                this.target_cells = [];
                if(this.board[row][col] != " " && this.player == this.colorOf(this.board[row][col]))
                {
                    this.active_cell = [row, col];
                    this.calculateValidMoves(row, col);
                }
                else
                    this.active_cell = "";
            }
        }
    }

    isValidMove(row, col)
    {
        let isValid = false;
        for(let i = 0;i < this.valid_cells.length;i ++)
        {
            if(this.valid_cells[i][0] == row && this.valid_cells[i][1] == col)
                isValid = true;
        }
        for(let i = 0;i < this.target_cells.length;i ++)
        {
            if(this.target_cells[i][0] == row && this.target_cells[i][1] == col)
                isValid = true;
        }
        return isValid;
    }

    calculateValidMoves(row, col)
    {
        let ptr = this.pAt(row, col);
        let pty = ptr.toLowerCase();
        // pawn moves
        if(pty == "p")
        {
            if(this.pAt(row - 1, col) == " ")
                this.valid_cells.push([row - 1, col]);
            if(this.pAt(row - 1, col) == " " && this.pAt(row - 2, col) == " " && row == 6)
                this.valid_cells.push([row - 2, col]);
            if(this.areOpposite(this.pAt(row - 1, col - 1), ptr))
                this.target_cells.push([row - 1, col - 1]);
            if(this.areOpposite(this.pAt(row - 1, col + 1), ptr))
                this.target_cells.push([row - 1, col + 1]);
        }
        //king moves
        if(pty == 'k')
        {
            if(this.pAt(row - 1, col - 1) == " ")
                this.valid_cells.push([row - 1, col - 1]);
            else if(this.areOpposite(this.pAt(row - 1, col - 1), ptr))
                this.target_cells.push([row - 1, col - 1]);
            if(this.pAt(row - 1, col) == " ")
                this.valid_cells.push([row - 1, col]);
            else if(this.areOpposite(this.pAt(row - 1, col), ptr))
                this.target_cells.push([row - 1, col]);
            if(this.pAt(row - 1, col + 1) == " ")
                this.valid_cells.push([row - 1, col + 1]);
            else if(this.areOpposite(this.pAt(row - 1, col + 1), ptr))
                this.target_cells.push([row - 1, col + 1]);
            if(this.pAt(row, col - 1) == " ")
                this.valid_cells.push([row, col - 1]);
            else if(this.areOpposite(this.pAt(row, col - 1), ptr))
                this.target_cells.push([row, col - 1]);
            if(this.pAt(row, col + 1) == " ")
                this.valid_cells.push([row, col + 1]);
            else if(this.areOpposite(this.pAt(row, col + 1), ptr))
                this.target_cells.push([row, col + 1]);
            if(this.pAt(row + 1, col - 1) == " ")
                this.valid_cells.push([row + 1, col - 1]);
            else if(this.areOpposite(this.pAt(row + 1, col - 1), ptr))
                this.target_cells.push([row + 1, col - 1]);
            if(this.pAt(row + 1, col) == " ")
                this.valid_cells.push([row + 1, col]);
            else if(this.areOpposite(this.pAt(row + 1, col), ptr))
                this.target_cells.push([row + 1, col]);
            if(this.pAt(row + 1, col + 1) == " ")
                this.valid_cells.push([row + 1, col + 1]);
            else if(this.areOpposite(this.pAt(row + 1, col + 1), ptr))
                this.target_cells.push([row + 1, col + 1]);
        }
        // rook moves
        if(pty == 'r')
        {
            for(let i = row + 1;i < row + 8;i ++)
            {
                if(this.pAt(i, col) == " ")
                    this.valid_cells.push([i, col]);
                else
                {
                    if(this.areOpposite(this.pAt(i, col), ptr))
                        this.target_cells.push([i, col]);
                    break;
                }
            }
            for(let i = row - 1;i >= row - 7;i --)
            {
                if(this.pAt(i, col) == " ")
                    this.valid_cells.push([i, col]);
                else
                {
                    if(this.areOpposite(this.pAt(i, col), ptr))
                        this.target_cells.push([i, col]);
                    break;
                }
            }
            for(let j = col + 1;j < col + 8;j ++)
            {
                if(this.pAt(row, j) == " ")
                    this.valid_cells.push([row, j]);
                else
                {
                    if(this.areOpposite(this.pAt(row, j), ptr))
                        this.target_cells.push([row, j]);
                    break;
                }
            }
            for(let j = col - 1;j >= col - 7;j --)
            {
                if(this.pAt(row, j) == " ")
                    this.valid_cells.push([row, j]);
                else
                {
                    if(this.areOpposite(this.pAt(row, j), ptr))
                        this.target_cells.push([row, j]);
                    break;
                }
            }
        }
        // bishop moves
        if(pty == 'b')
        {
            for(let i = 1;i < 8;i ++)
            {
                if(this.pAt(row + i, col + i) == " ")
                    this.valid_cells.push([row + i, col + i]);
                else
                {
                    if(this.areOpposite(this.pAt(row + i, col + i), ptr))
                        this.target_cells.push([row + i, col + i]);
                    break;
                }
            }
            for(let i = 1;i < 8;i ++)
            {
                if(this.pAt(row - i, col + i) == " ")
                    this.valid_cells.push([row - i, col + i]);
                else
                {
                    if(this.areOpposite(this.pAt(row - i, col + i), ptr))
                        this.target_cells.push([row - i, col + i]);
                    break;
                }
            }
            for(let i = 1;i < 8;i ++)
            {
                if(this.pAt(row - i, col - i) == " ")
                    this.valid_cells.push([row - i, col - i]);
                else
                {
                    if(this.areOpposite(this.pAt(row - i, col - i), ptr))
                        this.target_cells.push([row - i, col - i]);
                    break;
                }
            }
            for(let i = 1;i < 8;i ++)
            {
                if(this.pAt(row + i, col - i) == " ")
                    this.valid_cells.push([row + i, col - i]);
                else
                {
                    if(this.areOpposite(this.pAt(row + i, col - i), ptr))
                        this.target_cells.push([row + i, col - i]);
                    break;
                }
            }
        }
        // queen moves
        if(pty == 'q')
        {
            for(let i = row + 1;i < row + 8;i ++)
            {
                if(this.pAt(i, col) == " ")
                    this.valid_cells.push([i, col]);
                else
                {
                    if(this.areOpposite(this.pAt(i, col), ptr))
                        this.target_cells.push([i, col]);
                    break;
                }
            }
            for(let i = row - 1;i >= row - 7;i --)
            {
                if(this.pAt(i, col) == " ")
                    this.valid_cells.push([i, col]);
                else
                {
                    if(this.areOpposite(this.pAt(i, col), ptr))
                        this.target_cells.push([i, col]);
                    break;
                }
            }
            for(let j = col + 1;j < col + 8;j ++)
            {
                if(this.pAt(row, j) == " ")
                    this.valid_cells.push([row, j]);
                else
                {
                    if(this.areOpposite(this.pAt(row, j), ptr))
                        this.target_cells.push([row, j]);
                    break;
                }
            }
            for(let j = col - 1;j >= col - 7;j --)
            {
                if(this.pAt(row, j) == " ")
                    this.valid_cells.push([row, j]);
                else
                {
                    if(this.areOpposite(this.pAt(row, j), ptr))
                        this.target_cells.push([row, j]);
                    break;
                }
            }
            for(let i = 1;i < 8;i ++)
            {
                if(this.pAt(row + i, col + i) == " ")
                    this.valid_cells.push([row + i, col + i]);
                else
                {
                    if(this.areOpposite(this.pAt(row + i, col + i), ptr))
                        this.target_cells.push([row + i, col + i]);
                    break;
                }
            }
            for(let i = 1;i < 8;i ++)
            {
                if(this.pAt(row - i, col + i) == " ")
                    this.valid_cells.push([row - i, col + i]);
                else
                {
                    if(this.areOpposite(this.pAt(row - i, col + i), ptr))
                        this.target_cells.push([row - i, col + i]);
                    break;
                }
            }
            for(let i = 1;i < 8;i ++)
            {
                if(this.pAt(row - i, col - i) == " ")
                    this.valid_cells.push([row - i, col - i]);
                else
                {
                    if(this.areOpposite(this.pAt(row - i, col - i), ptr))
                        this.target_cells.push([row - i, col - i]);
                    break;
                }
            }
            for(let i = 1;i < 8;i ++)
            {
                if(this.pAt(row + i, col - i) == " ")
                    this.valid_cells.push([row + i, col - i]);
                else
                {
                    if(this.areOpposite(this.pAt(row + i, col - i), ptr))
                        this.target_cells.push([row + i, col - i]);
                    break;
                }
            }
        }
        // knight moves
        if(pty == 'n')
        {
            if(this.pAt(row - 2, col - 1) == " ")
                this.valid_cells.push([row - 2, col - 1]);
            else if(this.areOpposite(this.pAt(row - 2, col - 1), ptr))
                this.target_cells.push([row - 2, col - 1]);
            if(this.pAt(row - 2, col + 1) == " ")
                this.valid_cells.push([row - 2, col + 1]);
            else if(this.areOpposite(this.pAt(row - 2, col + 1), ptr))
                this.target_cells.push([row - 2, col + 1]);
            if(this.pAt(row - 1, col + 2) == " ")
                this.valid_cells.push([row - 1, col + 2]);
            else if(this.areOpposite(this.pAt(row - 1, col + 2), ptr))
                this.target_cells.push([row - 1, col + 2]);
            if(this.pAt(row + 1, col + 2) == " ")
                this.valid_cells.push([row + 1, col + 2]);
            else if(this.areOpposite(this.pAt(row + 1, col + 2), ptr))
                this.target_cells.push([row + 1, col + 2]);
            if(this.pAt(row + 2, col - 1) == " ")
                this.valid_cells.push([row + 2, col - 1]);
            else if(this.areOpposite(this.pAt(row + 2, col - 1), ptr))
                this.target_cells.push([row + 2, col - 1]);
            if(this.pAt(row + 2, col + 1) == " ")
                this.valid_cells.push([row + 2, col + 1]);
            else if(this.areOpposite(this.pAt(row + 2, col + 1), ptr))
                this.target_cells.push([row + 2, col + 1]);
            if(this.pAt(row - 1, col - 2) == " ")
                this.valid_cells.push([row - 1, col - 2]);
            else if(this.areOpposite(this.pAt(row - 1, col - 2), ptr))
                this.target_cells.push([row - 1, col - 2]);
            if(this.pAt(row + 1, col - 2) == " ")
                this.valid_cells.push([row + 1, col - 2]);
            else if(this.areOpposite(this.pAt(row + 1, col - 2), ptr))
                this.target_cells.push([row + 1, col - 2]);
        }
    }

    pAt(row, col)
    {
        if(row >= 0 && row < 8 && col >= 0 && col < 8)
            return this.board[row][col];
        else
            return "";
    }

    colorOf(piece)
    {
        if(piece >= 'a' && piece <= 'z')
            return 'black';
        else if(piece >= 'A' && piece <= 'Z')
            return 'white';
        else
            return '';
    }

    areOpposite(p1, p2)
    {
        if((this.colorOf(p1) == 'white' && this.colorOf(p2) == 'black') || (this.colorOf(p1) == 'black' && this.colorOf(p2) == 'white'))
            return true;
        else
            return false;
    }
}