import os
import yaml
import random
import hashlib
import threading
from typing import Dict, List, Union, Any


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
    

class chessbonMatch:
    """ chessbonMatch is a server side object for representing a chess match """
    def __init__(self, user_id_1: str, user_id_2: str) -> None:
        self.match_id = string_hash(user_id_1 + user_id_1)
        if random.random() > 0.5:
            self.user_ids = (user_id_1, user_id_2) # White, Black
        else:
            self.user_ids = (user_id_2, user_id_1)
        self.current_user = 0 # 0: W, 1: B
        self.match_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
    
    def get_details(self):
        return f"{self.user_ids[0]}|{self.user_ids[1]}|{self.current_user}|{self.match_fen}"
    
    def update_details(self, user_id: str, new_match_fen: str) -> bool:
        if user_id == self.user_ids[self.current_user]:
            self.current_user = (1 + self.current_user) % 2
            self.match_fen = new_match_fen
            return True
        else:
            return False
    
    def __str__(self) -> str:
        return self.get_details()
    
    def __repr__(self) -> str:
        return self.get_details()


def dump_yaml(path: str, data: Dict) -> None:
    with open(path, 'w') as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)

def load_yaml(path: str) -> Dict:
    with open(path, 'r') as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    return data

def get_env(return_json: bool = False) -> Union[Dict, List[Any]]:
    if "env.yaml" in os.listdir("."):
        src_dir = "."
    else:
        src_dir = "dev"
    envs = load_yaml(os.path.join(src_dir, "env.yaml"))
    if return_json:
        return envs
    else:
        return envs["ip_addr"], envs["port"], envs["buffer_size"]

def update_env(envs: Dict) -> None:
    if "env.yaml" in os.listdir("."):
        src_dir = "."
    else:
        src_dir = "dev"
    dump_yaml(os.path.join(src_dir, "env.yaml"), envs)
    
def string_hash(val: str) -> str:
    return hashlib.md5(val.encode()).hexdigest()

def change_server_admin(old_admin: str, new_admin: str) -> None:
    old_hash = string_hash(old_admin)
    envs = get_env(return_json=True)
    env_hash = envs["server_admin_hash"]
    if (old_hash == env_hash):
        new_hash = string_hash(new_admin)
        envs["server_admin_hash"] = new_hash
        update_env(envs)
        print("admin name updated successfully")
    else:
        print("old admin name incorrect")

if __name__ == "__main__":
    print(get_env())
    change_server_admin("akarsh", "aku")
