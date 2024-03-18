# Chessmen-Online

Multiplayer chess that two players can play over LAN. Created using Flask as backend and P5JS as frontend.  
The sprites used are taken from [chess.com](https://www.chess.com/).  

## Installation
Clone the [repo](https://github.com/saiakarsh193/Chess-Board-Online)
```bash
python3 -m pip install -r requirements.txt
```

## Usage
You can run the client app using,
```bash
python3 app.py
```

You can start the server using,
```bash
python3 backend.py start <password>
```

You can kill the server using,
```bash
python3 backend.py kill <password>
```

You can update the server password using,
```bash
python3 backend.py update_pass <password>
```

The env variables are stored in [env.yaml](env.yaml), change them accordingly.
```yaml
ip_addr: 10.10.10.2
port: 8031
buffer_size: 4096
server_password: 5d41402abc4b2a76b9719d911017c592
```

A preview of the frontend:  
<img src="assets/Screenshot from 2023-10-21 14-50-41.png" alt="screenshot1" width="650"/>
