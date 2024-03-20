# Chessmen-Online

Multiplayer chess that two players can play over LAN. Supports both CLI based and [P5JS](https://p5js.org/)-Flask GUI based gameplay. Use CLI for simple old-school terminal based interface. Use GUI for a more modern interactive interface.

> The sprites and GUI were taken and inspired by [chess.com](https://www.chess.com/).  

## Installation
Clone the [repo](https://github.com/saiakarsh193/chessmen-online/)
```bash
git clone https://github.com/saiakarsh193/chessmen-online/
cd chessmen-online
python3 -m pip install -r requirements.txt
```

## Usage

### client side
To start CLI,
```bash
python3 cli.py <username>
```

![cli_chess](/imgs/cli_chess.png)

To start GUI,
```bash
python3 app.py
```
![gui_chess](/imgs/gui_chess.png)

### dev side
You can start the server using,
```bash
# to start server
python3 backend.py start <password>

# to kill server
python3 backend.py kill <password>

# to change oauth for server
python3 backend.py update_pass <password>
```

The env variables are stored in [env.yaml](env.yaml), change them accordingly.
```yaml
ip_addr: 10.2.128.150
port: 8001
buffer_size: 4096
server_password: 5d41402abc4b2a76b9719d911017c592
```
