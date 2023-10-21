let cx, cy;
let board;
let pieces_img;
let img_sheet;
let myuid;

let connect_time = 0;
let isconnect = false;

function preload()
{
    img_sheet = loadImage("/static/piece_sheet.png");
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