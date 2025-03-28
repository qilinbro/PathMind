import requests
import json
from typing import Dict, List

BASE_URL = "http://localhost:8000"

def test_get_questions():
    """Test getting assessment questions"""
    response = requests.get(f"{BASE_URL}/api/v1/assessment/questions/")
    assert response.status_code == 200
    questions = response.json()
    assert len(questions) > 0
    print(f"Successfully retrieved {len(questions)} questions")
    return questions

def test_submit_assessment(questions: List[Dict]):
    """Test submitting assessment responses"""
    # Prepare test responses
    responses = []
    for question in questions:
        response = {
            "question_id": question["id"],
            "response_value": {"scale": 4},  # Test with "Agree" response
            "response_time": 2.5  # Test with 2.5 seconds response time
        }
        responses.append(response)
    
    # Submit assessment
    payload = {
        "user_id": 1,  # Test user ID
        "responses": responses
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/assessment/submit/",
        json=payload
    )
    assert response.status_code == 200
    result = response.json()
    print("Assessment submission successful")
    print("Learning style results:", json.dumps(result, indent=2))
    return result

def run_tests():
    """Run all API tests"""
    print("\n=== Starting API Tests ===\n")
    
    try:
        # Test getting questions
        questions = test_get_questions()
        print("\nQuestion retrieval test passed ✓")
        
        # Test submitting assessment
        result = test_submit_assessment(questions)
        print("\nAssessment submission test passed ✓")
        
        print("\n=== All Tests Passed ===")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise e

if __name__ == "__main__":
    run_tests()