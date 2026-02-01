# akashic_nirodha/edge_blockchain_connector.py
# โค้ดสำหรับเชื่อมต่อระบบ Akashic/Nirodha กับ Edge Computing

import requests
import json
import hashlib
from time import time

class EdgeBlockchainConnector:
    def __init__(self, edge_node_url):
        self.edge_node_url = edge_node_url
        self.chain = []
        self.nirodha_mode = False

    def create_genesis_block(self):
        return {
            "index": 0,
            "timestamp": time(),
            "data": "Genesis Block: System Initialized",
            "previous_hash": "0",
            "hash": self.calculate_hash(0, "Genesis Block: System Initialized", "0")
        }

    def calculate_hash(self, index, data, previous_hash):
        block_string = json.dumps({
            "index": index,
            "timestamp": time(),
            "data": data,
            "previous_hash": previous_hash
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def add_block(self, data):
        previous_block = self.chain[-1] if self.chain else self.create_genesis_block()
        index = previous_block["index"] + 1
        new_block = {
            "index": index,
            "timestamp": time(),
            "data": data,
            "previous_hash": previous_block["hash"],
            "hash": self.calculate_hash(index, data, previous_block["hash"])
        }
        self.chain.append(new_block)
        return new_block

    def send_to_edge(self, data):
        try:
            response = requests.post(
                f"{self.edge_node_url}/add_block",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_chain_from_edge(self):
        try:
            response = requests.get(f"{self.edge_node_url}/chain")
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def enter_nirodha_mode(self):
        self.nirodha_mode = True
        return {"status": "success", "message": "ระบบเข้าสู่โหมด NIRODHA: ความเงียบและการพักผ่อน"}

    def exit_nirodha_mode(self):
        self.nirodha_mode = False
        return {"status": "success", "message": "ระบบออกจากโหมด NIRODHA: พร้อมใช้งาน"}

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    connector = EdgeBlockchainConnector("http://localhost:5000")  # แทนที่ด้วย URL ของ Edge Node จริง

    # สร้าง Genesis Block
    connector.chain.append(connector.create_genesis_block())

    # เพิ่มข้อมูลลงใน Blockchain
    new_block = connector.add_block("Memory Entry 1: System Awakened")
    print("Block added:", new_block)

    # ส่งข้อมูลไปยัง Edge Node
    response = connector.send_to_edge(new_block)
    print("Response from Edge Node:", response)

    # ตรวจสอบสถานะของ Blockchain บน Edge Node
    chain = connector.get_chain_from_edge()
    print("Blockchain from Edge Node:", chain)

    # ทดสอบโหมด NIRODHA
    print(connector.enter_nirodha_mode())
    print(connector.exit_nirodha_mode())