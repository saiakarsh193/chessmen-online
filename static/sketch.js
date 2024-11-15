let cx, cy;
let board;
let pieces_img;
let img_sheet;
let myuid;

let connect_time = 0;
let isconnect = false;

async function server_request(url = '', data = {})
{
    const response = await fetch(url, {
    method: 'POST',
    mode: 'cors',
    cache: 'no-cache',
    credentials: 'same-origin',
    headers: {
        'Content-Type': 'application/json'
    },
    redirect: 'follow',
    referrerPolicy: 'no-referrer',
    body: JSON.stringify(data)
    });
    return response.json();
}

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

function preload()
{
    img_sheet = loadImage("/imgs/piece_sheet.png");
    postData('/ping', {'request': 'get_user_id'})
    .then((data) => {
        myuid = data['response'];
    });
    postData('/ping', {'request': 'allocate'})
    .then((data) => {
        print(data['response']);
    });
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

    board = new Board(pieces_img, myuid);
}

function draw()
{
    if(millis() - connect_time > 1 * 1000 && !isconnect)
    {
        connect_time = millis();
        postData('/ping', {'request': 'status'})
        .then((data) => {
            return data['response'];
        })
        .then((resp) => {
            print(resp);
            if(resp != '<waiting for game>')
            {
                isconnect = true;
                postData('/ping', {'request': 'getfen'})
                .then((data) => {
                    return data['response'];
                })
                .then((resp) => {
                    let srep = resp.substring(1, resp.length - 1).split(' :: ');
                    board.assign(srep[0]);
                });
            }
        });
    }
    translate(cx, cy);
    board.draw();
}

function mouseClicked()
{
    if(isconnect)
    {
        postData('/ping', {'request': 'status'})
        .then((data) => {
            return data['response'];
        })
        .then((resp) => {
            if(resp == '<your turn>')
                board.click(mouseX - cx, mouseY - cy);
        });
    }
}