# Chessmen-Online

Multiplayer chess that two players can play over LAN. Supports both CLI based and [Avour](https://github.com/saiakarsh193/avour) GUI based gameplay. Use CLI for simple old-school terminal based interface. Use GUI for a more modern interactive interface. Checkout [git submodule](https://github.blog/open-source/git/working-with-submodules/) for more info on recursive cloning.

> The sprites and GUI were taken and inspired by [chess.com](https://www.chess.com/).  

## Installation
Clone the [repo](https://github.com/saiakarsh193/chessmen-online/)
```bash
git clone --recursive https://github.com/saiakarsh193/chessmen-online/
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
python3 gui.py <username>
```
![gui_chess](/imgs/gui_chess.png)

### server side
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

To get the IP Address:
- For Linux, use `ip addr`
- For MACOS, use `ipconfig getsummary en0` (assuming `en0` is the LAN source)