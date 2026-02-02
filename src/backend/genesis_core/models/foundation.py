import time
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from enum import Enum

# ใช้ Enum เพื่อความชัดเจนและรวดเร็วในการตรวจสอบประเภทเจตจำนง
class IntentType(str, Enum):
    COGNITIVE_QUERY = "COGNITIVE_QUERY"  # คำถามที่ต้องใช้การคิดวิเคราะห์
    SYSTEM_SIGNAL = "SYSTEM_SIGNAL"      # สัญญาณระบบ (เช่น Heartbeat)
    MOTOR_COMMAND = "MOTOR_COMMAND"      # คำสั่งควบคุม (เช่น แสดงผล UI)

@dataclass(frozen=True, slots=True)
class IntentVector:
    """
    โครงสร้างข้อมูลหลักที่ใช้สื่อสารภายในระบบ (Intent-driven)
    ถูกออกแบบให้เป็น Immutable (แก้ไขไม่ได้) เพื่อความปลอดภัยและ Thread-safety
    """
    vector_id: str
    origin_agent: str
    intent_type: IntentType
    payload: Dict[str, Any] = field(default_factory=dict)

    # Context คือบริบทแวดล้อม (แสง, เสียง, อารมณ์)
    context: Dict[str, float] = field(default_factory=dict)

    timestamp: float = field(default_factory=time.time)

    @property
    def entropy(self) -> float:
        """คำนวณค่าความปั่นป่วน (Turbulence) ของเจตจำนงนี้ (จำลอง)"""
        return self.context.get("turbulence", 0.0)

    def to_json(self) -> str:
        """แปลงเป็น JSON string อย่างรวดเร็ว"""
        data = {
            "id": self.vector_id,
            "origin": self.origin_agent,
            "type": self.intent_type.value,
            "payload": "****PII REMOVED****", # จำลอง Identity Annihilation
            "ts": self.timestamp
        }
        return json.dumps(data)

@dataclass(frozen=True, slots=True)
class AkashicEnvelope:
    """
    ซองจดหมายที่ห่อหุ้มข้อมูลดิบ (Devordota) เพื่อส่งเข้า AetherBus
    ใช้เทคนิค Hashing เพื่อยืนยันความถูกต้อง (Integrity)
    """
    envelope_id: str
    content: Any
    signature: str

    @staticmethod
    def seal(content: Any, secret_key: str = "genesis-key") -> 'AkashicEnvelope':
        """สร้างซองจดหมายและประทับตรา (Seal)"""
        # จำลองการสร้าง Hash Signature
        content_str = str(content)
        signature = hashlib.sha256(f"{content_str}{secret_key}".encode()).hexdigest()
        return AkashicEnvelope(
            envelope_id=hashlib.md5(content_str.encode()).hexdigest(),
            content=content,
            signature=signature
        )
