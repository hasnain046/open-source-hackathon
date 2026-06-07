# Module: tests.test_copilot
# Description: Automated unit and integration tests for Phase 11: AI Economist Copilot.

import os
import sys
import unittest
import uuid
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.core.database import Base
from app.models.log import CopilotConversation, CopilotMessage
from app.models.user import User
from app.schemas.copilot import (
    ChatResponseSchema,
    ConversationListResponseSchema,
    ChatMessageResponseSchema
)
from app.services.copilot_service import CopilotService
from app.api.deps import get_current_user, get_db

SQLITE_PATH = "sqlite:///" + os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "local_sqlite.db")).replace("\\", "/")

# Mock user for copilot
mock_copilot_user_id = uuid.uuid4()
mock_user = User(
    id=mock_copilot_user_id,
    email="analyst-copilot@inflationiq.ai",
    full_name="Copilot Tester",
    role="analyst",
    is_active=True,
    created_at=datetime.utcnow()
)


class TestAIEconomistCopilot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(SQLITE_PATH)
        Base.metadata.create_all(bind=cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)
        
    def setUp(self):
        self.db = self.Session()
        self.client = TestClient(app)
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: self.db
        
    def tearDown(self):
        self.db.close()
        app.dependency_overrides.clear()

    def test_context_assembler(self):
        """1. Context Assembler Assertion: Grounding context string builds successfully."""
        context_string, sources, conf_score, conf_indicator, citations = CopilotService.assemble_context(self.db)
        
        self.assertIsNotNone(context_string)
        self.assertTrue(isinstance(sources, list))
        self.assertTrue(0.0 <= conf_score <= 1.0)
        self.assertIn(conf_indicator, ["High", "Moderate", "Low"])
        
        # Verify that all 5 engines are represented in sources metadata
        engine_names = set(s["engine"] for s in sources)
        expected_engines = {"Forecast Engine", "SHAP Engine", "News Intelligence", "Currency Prediction", "RAG Knowledge Base"}
        self.assertTrue(expected_engines.issubset(engine_names), f"Missing engines: {expected_engines - engine_names}")

    def test_nlg_fallback_modes_and_grounding(self):
        """2. NLG Fallback Verification: Test modes formatting, source attributions, and grounding guard."""
        # A. Test Grounding Guard: if a source is unavailable, assistant returns grounding warnings
        empty_sources = [
            {"engine": "Forecast Engine", "source_type": "forecasts", "status": "Unavailable"},
            {"engine": "SHAP Engine", "source_type": "forecast_explainability", "status": "Unavailable"},
            {"engine": "News Intelligence", "source_type": "news_signals", "status": "Unavailable"},
            {"engine": "Currency Prediction", "source_type": "currency_data", "status": "Unavailable"}
        ]
        
        reply_no_shap = CopilotService.generate_reply_via_nlg("Why is inflation projected to increase?", "analyst", "", empty_sources)
        self.assertIn("unavailable", reply_no_shap.lower())
        self.assertIn("shap", reply_no_shap.lower())
        
        # B. Test Modes formatting (Economist vs Executive vs Analyst)
        valid_sources = [
            {"engine": "Forecast Engine", "source_type": "forecasts", "status": "Retrieved"},
            {"engine": "SHAP Engine", "source_type": "forecast_explainability", "status": "Retrieved"},
            {"engine": "News Intelligence", "source_type": "news_signals", "status": "Retrieved"},
            {"engine": "Currency Prediction", "source_type": "currency_data", "status": "Retrieved"}
        ]
        
        # Economist mode should be theoretical
        econ_reply = CopilotService.generate_reply_via_nlg("Why is inflation changing?", "economist", "context", valid_sources)
        self.assertIn("transmission", econ_reply.lower())
        self.assertIn("structure", econ_reply.lower())
        
        # Executive mode should have bullet points
        exec_reply = CopilotService.generate_reply_via_nlg("Why is inflation changing?", "executive", "context", valid_sources)
        self.assertIn("•", exec_reply)
        self.assertIn("takeaway", exec_reply.lower())
        
        # Analyst mode should have data rates
        analyst_reply = CopilotService.generate_reply_via_nlg("Why is inflation changing?", "analyst", "context", valid_sources)
        self.assertIn("contribution", analyst_reply.lower())
        self.assertIn("4.41%", analyst_reply)

    def test_conversation_persistence_and_api(self):
        """3. Conversation Memory & API: Assert thread history writes and chat API schema compatibility."""
        headers = {"Authorization": "Bearer mock_token"}
        
        # A. Send first message (Starts conversation)
        payload = {
            "message": "Why is food inflation high?",
            "mode": "analyst"
        }
        res_chat = self.client.post("/api/v1/copilot/chat", json=payload, headers=headers)
        self.assertEqual(res_chat.status_code, 200)
        chat_data = res_chat.json()
        
        # Validate schema
        parsed_chat = ChatResponseSchema(**chat_data)
        conv_id = parsed_chat.conversation_id
        
        # B. Send second message on same thread (Conversational continuity)
        payload2 = {
            "conversation_id": str(conv_id),
            "message": "What about currency rates?",
            "mode": "executive"
        }
        res_chat2 = self.client.post("/api/v1/copilot/chat", json=payload2, headers=headers)
        self.assertEqual(res_chat2.status_code, 200)
        chat_data2 = res_chat2.json()
        parsed_chat2 = ChatResponseSchema(**chat_data2)
        
        # Verify message count in history has user/assistant message pairs
        self.assertTrue(len(parsed_chat2.history) >= 4)
        
        # C. Retrieve conversations list
        res_list = self.client.get("/api/v1/copilot/conversations", headers=headers)
        self.assertEqual(res_list.status_code, 200)
        list_data = res_list.json()
        self.assertTrue(len(list_data) > 0)
        for item in list_data:
            ConversationListResponseSchema(**item)
            
        # D. Retrieve message logs
        res_msg = self.client.get(f"/api/v1/copilot/conversations/{conv_id}/messages", headers=headers)
        self.assertEqual(res_msg.status_code, 200)
        msg_data = res_msg.json()
        self.assertTrue(len(msg_data) >= 4)
        for item in msg_data:
            ChatMessageResponseSchema(**item)


if __name__ == "__main__":
    unittest.main()
