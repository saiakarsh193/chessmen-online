# Chessmen-Online

Chessmen Online is a multiplayer chess platform where two players can play each other over a LAN. It supports both CLI based and [Avour](https://github.com/saiakarsh193/avour) GUI based gameplay. Use CLI for simple old-school terminal based interface. Use GUI for a more modern interactive interface. Checkout [git submodule](https://github.blog/open-source/git/working-with-submodules/) for more info on recursive cloning.

> The sprites and GUI were taken and inspired by [chess.com](https://www.chess.com/).  

## Installation
Clone the [repo](https://github.com/saiakarsh193/chessmen-online/)
```bash
git clone --recursive https://github.com/saiakarsh193/chessmen-online/
cd chessmen-online
python3 -m pip install -r requirements.txt
```

## Usage

The network interface is a simple server-client setup. Therefore one system needs to act as a common server (this server system can also host a client if required). All systems should be on the same LAN (Local Area Network) to be able to communicate with each other. The `ip_addr` and `port` in `env.yaml` for each system should be set to the IP address and port of the server system.

The env variables are stored in [env.yaml](env.yaml), change them accordingly.
```yaml
ip_addr: 10.2.128.150   # IP address of the server
port: 8001              # port of the server
buffer_size: 4096       # message buffer size (not required to change)
server_password: 5d41402abc4b2a76b9719d911017c592 # server password hash (dont change manually)
```

To get the IP Address:
- For Linux, use `ip addr`
- For MACOS, use `ipconfig getsummary en0` (assuming `en0` is the LAN source)

### server side

```bash
# to start server
python3 backend.py start <password>

# to kill server
python3 backend.py kill <password>

# to change oauth for server
python3 backend.py update_pass <password>
```

### client side

To start CLI,
```bash
python3 cli.py --user_id <username>

# for local multiplayer
python3 cli.py --local
```
![cli_chess](/imgs/cli_chess.png)

To start GUI,
```bash
python3 gui.py --user_id <username>

# for local multiplayer
python3 gui.py --local
```
![gui_chess](/imgs/gui_chess.png)

### Issues
- To fix mouse click issue in Mac: [[171]](https://github.com/pyglet/pyglet/issues/171)
  ```python
    import pyglet
    pyglet.options['osx_alt_loop'] = True
  ```