# Chess-Board-Online (CHESSBON)

Multiplayer Chess that two players can play over LAN. Created using Flask as backend and P5JS as frontend.  
The sprites used are taken from [chess.com](https://www.chess.com/).  

## Installation
Clone the [repo](https://github.com/saiakarsh193/Chess-Board-Online)
```bash
git clone https://github.com/saiakarsh193/Chess-Board-Online
cd Chess-Board-Online
python3 -m pip install -r requirements.txt
```

## Usage
You can run the client app using,
```bash
python3 app.py
```

You can run the server side using,
```bash
python3 dev/server.py <admin_name>
```

The env variables are stored in [env.yaml](dev/env.yaml), change them accordingly.
```yaml
ip_addr: 10.2.7.171
port: 2000
buffer_size: 4096
server_admin_hash: b6f2387752c5a998dfa2c4610a001745 # for server admin auth
```

You need server `admin_name` to start the server. You can change it using,
```python3
from dev.utils import change_server_admin

change_server_admin("<old_admin_name>", "<new_admin_name>")
```

A preview of the frontend:  
<img src="assets/Screenshot from 2023-10-21 14-50-41.png" alt="screenshot1" width="650"/>
