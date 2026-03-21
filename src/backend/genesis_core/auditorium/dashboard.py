import datetime
import logging

from .memory_audit import PanGenesisAuditor
from .bus_audit import AetherBusAuditor
from .perception_audit import ChromaticSanctumAuditor
from .dual_architecture import DualArchitectureAuditor
from .cognition_audit import StateActAuditor
from .consciousness_audit import AwakeningCycleAuditor
from .interface_audit import LivingGunUIAuditor
from .constitution_audit import ConstitutionAuditor
from .hive_audit import HiveMindAuditor

logger = logging.getLogger("AetheriumHealthDashboard")

class AetheriumEmergencyProtocols:
    def __init__(self, engine_ref):
        self.engine = engine_ref

    def handle_constitutional_crisis(self, violation_report):
        response = {
            "actions_taken": [],
            "status": "active"
        }
        if violation_report.get('critical_violations', 0) > 0:
            # Force Nirodha
             if hasattr(self.engine, 'enter_nirodha'):
                 logger.critical("🚨 CONSTITUTIONAL CRISIS: Forcing Nirodha State")
                 self.engine.enter_nirodha()
                 response["actions_taken"].append("forced_nirodha")
                 response["status"] = "nirodha"
        return response

class AetheriumHealthDashboard:
    def __init__(self, engine_ref):
        self.engine = engine_ref

        # Auditors
        self.memory = PanGenesisAuditor()
        self.bus = AetherBusAuditor()
        self.perception = ChromaticSanctumAuditor()
        self.dual = DualArchitectureAuditor()
        self.cognition = StateActAuditor()
        self.consciousness = AwakeningCycleAuditor()
        self.interface = LivingGunUIAuditor()
        self.constitution = ConstitutionAuditor()
        self.hive = HiveMindAuditor()

        self.emergency = AetheriumEmergencyProtocols(engine_ref)

    async def generate_comprehensive_report(self):
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "overall_health_score": 0.0,
            "components": {},
            "emergency_alerts": []
        }

        # 1. Gather Data
        try:
            # Sync Checks
            report["components"]["memory"] = self.memory.audit_eternal_memory()
            report["components"]["bus"] = self.bus.audit_lightning_speed()

            # Interface check needs visual params
            last_vp = getattr(self.engine, 'last_visual_params', {})
            report["components"]["interface"] = self.interface.audit_living_skin(last_vp)

            report["components"]["constitution"] = self.constitution.audit_immutable_principles({})
            report["components"]["hive"] = self.hive.audit_organizational_health()
            report["components"]["cognition"] = self.cognition.audit_mindful_thinking()
            report["components"]["consciousness"] = self.consciousness.monitor_consciousness_cycle()
            report["components"]["perception"] = self.perception.audit_mathematical_eye()

            # Dual Architecture
            current_intent = str(getattr(self.engine, "current_intent", ""))
            current_action = str(getattr(self.engine, "current_action", ""))
            report["components"]["dual_architecture"] = self.dual.check_alignment(current_intent, current_action)

            # 2. Calculate Score
            scores = []
            for key, comp in report["components"].items():
                comp_score = 0.0
                count = 0
                metrics = comp.get("metrics", {})
                for m_key, m_val in metrics.items():
                    if isinstance(m_val, (int, float)):
                        comp_score += float(m_val)
                        count += 1
                    elif isinstance(m_val, bool):
                        comp_score += 1.0 if m_val else 0.0
                        count += 1

                if count > 0:
                    final_comp_score = comp_score / count
                else:
                    final_comp_score = 0.0

                scores.append(final_comp_score)
                comp["health_score"] = round(final_comp_score, 2)

            if scores:
                report["overall_health_score"] = round(sum(scores) / len(scores), 2)

            # 3. Emergency Check
            # If health is critically low (< 0.3)
            if report["overall_health_score"] < 0.3:
                 res = self.emergency.handle_constitutional_crisis({'critical_violations': 1})
                 report["emergency_response"] = res

        except Exception as e:
            logger.error(f"Dashboard Generation Error: {e}")
            report["error"] = str(e)

        return report
