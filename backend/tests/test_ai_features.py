import pytest
from httpx import AsyncClient
import json
from app.main import app
from app.core.config import settings

# Test data
test_content = {
    "title": "Visual Programming Concepts",
    "description": "Learn programming through visual diagrams and animations",
    "content_type": "interactive",
    "subject": "computer_science",
    "difficulty_level": 2,
    "content_data": {
        "interactive_url": "https://example.com/visual-programming",
        "duration": 1800,
        "interactive_elements": ["animations", "diagrams", "exercises"]
    },
    "visual_affinity": 85.0,
    "auditory_affinity": 30.0,
    "kinesthetic_affinity": 55.0,
    "reading_affinity": 40.0,
    "author": "Code Academy",
    "tags": ["Programming", "Visual Learning", "Interactive"]
}

test_assessment_submission = {
    "user_id": 1,
    "responses": [
        {
            "question_id": 1,
            "response_value": {"answer": "5", "confidence": "high"},
            "response_time": 8.5
        },
        {
            "question_id": 2,
            "response_value": {"answer": "2", "confidence": "medium"},
            "response_time": 10.2
        }
    ]
}

@pytest.mark.asyncio
async def test_ai_learning_style_assessment():
    """Test AI-powered learning style assessment analysis"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create test content
        response = await client.post("/api/v1/content/", json=test_content)
        assert response.status_code == 200
        
        # Submit assessment
        response = await client.post("/api/v1/assessment/submit/", json=test_assessment_submission)
        assert response.status_code == 200
        
        result = response.json()
        assert "learning_style_result" in result
        assert "recommendations" in result
        
        # Verify learning style analysis
        learning_style = result["learning_style_result"]
        assert "visual_score" in learning_style
        assert "auditory_score" in learning_style
        assert "dominant_style" in learning_style

@pytest.mark.asyncio
async def test_ai_content_recommendations():
    """Test AI-powered content recommendations"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Request recommendations
        recommendation_request = {
            "user_id": 1,
            "limit": 3,
            "exclude_viewed": False
        }
        
        response = await client.post("/api/v1/content/recommendations", json=recommendation_request)
        assert response.status_code == 200
        
        result = response.json()
        assert "recommendations" in result
        assert "recommendation_factors" in result
        
        # Verify recommendation quality
        recommendations = result["recommendations"]
        assert len(recommendations) > 0
        for rec in recommendations:
            assert "content" in rec
            assert "explanation" in rec
            assert "approach_suggestion" in rec

@pytest.mark.asyncio
async def test_ai_personalization():
    """Test AI personalization features"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Get user's learning progress
        response = await client.get("/api/v1/assessment/progress/1")
        assert response.status_code == 200
        
        result = response.json()
        assert "current_learning_style" in result
        assert "progress_metrics" in result
        assert "improvement_suggestions" in result

@pytest.mark.asyncio
async def test_zhipuai_integration():
    """Test ZhipuAI API integration for recommendations"""
    if not settings.ZHIPU_API_KEY:
        pytest.skip("ZhipuAI API key not configured")
        
    async with AsyncClient(app=app, base_url="http://test") as client:
        recommendation_request = {
            "user_id": 1,
            "subject": "computer_science",
            "content_type": "interactive",
            "limit": 2,
            "exclude_viewed": False
        }
        
        response = await client.post("/api/v1/content/recommendations", json=recommendation_request)
        assert response.status_code == 200
        
        result = response.json()
        recommendations = result["recommendations"]
        
        # Verify AI-generated explanations
        for rec in recommendations:
            assert len(rec["explanation"]) > 0
            assert len(rec["approach_suggestion"]) > 0

@pytest.mark.asyncio
async def test_learning_behavior_analysis():
    """Test AI-powered learning behavior analysis"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Submit learning behavior data
        behavior_data = {
            "user_id": 1,
            "content_interactions": [
                {
                    "content_id": 1,
                    "time_spent": 1200,
                    "interaction_type": "video_watch",
                    "progress": 0.8,
                    "engagement_metrics": {
                        "pauses": 3,
                        "rewinds": 2,
                        "notes_taken": True
                    }
                }
            ]
        }
        
        response = await client.post("/api/v1/analytics/behavior", json=behavior_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "behavior_patterns" in result
        assert "engagement_level" in result
        assert "study_habits" in result
        assert "improvement_areas" in result

@pytest.mark.asyncio
async def test_weakness_identification():
    """Test AI-powered learning weakness identification"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/analytics/weaknesses/1")
        assert response.status_code == 200
        
        result = response.json()
        assert "weak_areas" in result
        assert "strength_areas" in result
        assert "improvement_plan" in result
        
        # Verify detailed analysis
        for area in result["weak_areas"]:
            assert "topic" in area
            assert "confidence_level" in area
            assert "suggested_resources" in area

@pytest.mark.asyncio
async def test_adaptive_testing():
    """Test AI-powered adaptive testing system"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Request adaptive test
        test_request = {
            "user_id": 1,
            "subject": "computer_science",
            "topic": "programming_basics",
            "difficulty": "auto"
        }
        
        response = await client.post("/api/v1/assessment/adaptive-test", json=test_request)
        assert response.status_code == 200
        
        result = response.json()
        assert "questions" in result
        assert "adaptive_logic" in result
        assert "estimated_difficulty" in result

@pytest.mark.asyncio
async def test_mistake_analysis():
    """Test AI-powered mistake analysis"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/analytics/mistakes/1")
        assert response.status_code == 200
        
        result = response.json()
        assert "common_mistakes" in result
        assert "mistake_patterns" in result
        assert "remediation_plan" in result

if __name__ == "__main__":
    pytest.main(["-v", "test_ai_features.py"])
