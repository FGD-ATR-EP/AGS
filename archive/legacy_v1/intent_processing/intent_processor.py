# intent_processing/intent_processor.py
# โค้ดสำหรับประมวลผล Intent Vectors

import json
import random
import time

class IntentProcessor:
    def __init__(self):
        """
        Initialize a new IntentProcessor instance.
        
        Sets up an empty `intent_history` list to record processed intent vectors and their results.
        """
        self.intent_history = []

    def process_intent(self, intent_vector):
        # ประมวลผล Intent Vector
        intent_type = intent_vector.get("intent_type", "unknown")
        user_id = intent_vector.get("user_id", "unknown")

        # สร้างผลลัพธ์ตาม Intent Type
        if intent_type == "awaken":
            result = {"status": "success", "action": "system_awakened", "message": "ระบบถูกปลุก"}
        elif intent_type == "sleep":
            result = {"status": "success", "action": "system_sleep", "message": "ระบบเข้าสู่โหมด NIRODHA"}
        else:
            result = {"status": "error", "action": "unknown_intent", "message": "ไม่ทราบ Intent นี้"}

        # บันทึกประวัติ Intent
        self.intent_history.append({
            "intent_vector": intent_vector,
            "result": result,
            "timestamp": json.dumps({"time": time.time()})
        })

        return result

    def get_intent_history(self):
        return self.intent_history

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    processor = IntentProcessor()

    # ตัวอย่าง Intent Vector
    intent_vector = {
        "intent_type": "awaken",
        "user_id": "user123",
        "context": {"location": "home", "time": "morning"}
    }

    # ประมวลผล Intent Vector
    result = processor.process_intent(intent_vector)
    print("Intent Processing Result:", result)

    # แสดงประวัติ Intent
    print("Intent History:", processor.get_intent_history())