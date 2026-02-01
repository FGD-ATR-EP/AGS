# edge_computing/edge_connector.py
# โค้ดสำหรับเชื่อมต่อกับ Edge Computing

import requests
import json

class EdgeConnector:
    def __init__(self, edge_node_url):
        self.edge_node_url = edge_node_url

    def send_to_edge(self, data):
        try:
            response = requests.post(
                f"{self.edge_node_url}/process",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_edge_status(self):
        try:
            response = requests.get(f"{self.edge_node_url}/status")
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    edge_connector = EdgeConnector("http://localhost:5000")  # แทนที่ด้วย URL ของ Edge Node จริง

    # ส่งข้อมูลไปยัง Edge Node
    data = {"intent": "awaken", "user_id": "user123"}
    response = edge_connector.send_to_edge(data)
    print("Response from Edge Node:", response)

    # ตรวจสอบสถานะของ Edge Node
    status = edge_connector.get_edge_status()
    print("Edge Node Status:", status)