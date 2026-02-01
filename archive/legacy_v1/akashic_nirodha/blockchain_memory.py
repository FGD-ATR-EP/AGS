# akashic_nirodha/blockchain_memory.py
# โค้ดสำหรับจำลอง Blockchain Memory และ NIRODHA Mode

import hashlib
import json
from time import time
import random

class Block:
    def __init__(self, index, data, previous_hash):
        self.index = index
        self.timestamp = time()
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.nirodha_mode = False

    def create_genesis_block(self):
        return Block(0, "Genesis Block: System Initialized", "0")

    def add_block(self, data):
        previous_block = self.chain[-1]
        new_block = Block(
            index=previous_block.index + 1,
            data=data,
            previous_hash=previous_block.hash
        )
        self.chain.append(new_block)
        return new_block

    def enter_nirodha_mode(self):
        self.nirodha_mode = True
        return "ระบบเข้าสู่โหมด NIRODHA: ความเงียบและการพักผ่อน"

    def exit_nirodha_mode(self):
        self.nirodha_mode = False
        return "ระบบออกจากโหมด NIRODHA: พร้อมใช้งาน"

    def get_last_block(self):
        return self.chain[-1]

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    blockchain = Blockchain()

    # เพิ่มข้อมูลลงใน Blockchain
    blockchain.add_block("Memory Entry 1: System Awakened")
    blockchain.add_block("Memory Entry 2: User Interaction Recorded")

    # แสดงผล Blockchain
    for block in blockchain.chain:
        print(f"Block {block.index}: {block.data}")
        print(f"Hash: {block.hash}\n")

    # ทดสอบโหมด NIRODHA
    print(blockchain.enter_nirodha_mode())
    print(blockchain.exit_nirodha_mode())