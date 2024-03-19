import os
import yaml
import random
import hashlib
import threading
from typing import Dict, Tuple, Union, Any


class sharedMem:
    """ sharedMem is a small wrapper on threading mutex object """
    def __init__(self, data: Any) -> None:
        self.data = data
        self.mutex = threading.Lock()

    def lock(self) -> None:
        self.mutex.acquire()

    def unlock(self) -> None:
        self.mutex.release()
    
    def __str__(self) -> str:
        return str(self.data)

def load_yaml(path: str) -> Dict:
    with open(path, 'r') as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    return data

def dump_yaml(path: str, data: Dict) -> None:
    with open(path, 'w') as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)

def get_env(path = ".", return_json: bool = False) -> Union[Dict, Tuple[str, str, str, str]]:
    envs = load_yaml(os.path.join(path, "env.yaml"))
    if return_json:
        return envs
    return envs["ip_addr"], envs["port"], envs["buffer_size"], envs["server_password"]

def update_env(envs: Dict, path = ".") -> None:
    dump_yaml(os.path.join(path, "env.yaml"), envs)

def random_hash(slen: int) -> str:
    return hex(random.getrandbits(slen * 5))[2: slen + 2]

def string_hash(val: str) -> str:
    return hashlib.md5(val.encode()).hexdigest()
