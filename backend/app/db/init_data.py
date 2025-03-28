from sqlalchemy.orm import Session
from app.models.user import User
from app.models.learning_assessment import AssessmentQuestion
from app.models.content import LearningContent, ContentTag
from app.core.config import settings
from app.db.session import init_db, SessionLocal

def init_content_tags(db: Session) -> None:
    """Initialize content tags"""
    tags = [
        {"name": "Mathematics", "description": "Mathematical concepts and problems"},
        {"name": "Programming", "description": "Programming and software development"},
        {"name": "Science", "description": "Scientific concepts and experiments"},
        {"name": "Language", "description": "Language learning materials"},
        {"name": "Beginner", "description": "Content suitable for beginners"},
        {"name": "Intermediate", "description": "Content for intermediate learners"},
        {"name": "Advanced", "description": "Advanced level content"}
    ]
    
    for tag_data in tags:
        exists = db.query(ContentTag).filter_by(name=tag_data["name"]).first()
        if not exists:
            tag = ContentTag(**tag_data)
            db.add(tag)
    
    db.commit()
    print("Content tags initialized successfully")

def init_sample_content(db: Session) -> None:
    """Initialize sample learning content"""
    
    # Get tags
    math_tag = db.query(ContentTag).filter_by(name="Mathematics").first()
    prog_tag = db.query(ContentTag).filter_by(name="Programming").first()
    beginner_tag = db.query(ContentTag).filter_by(name="Beginner").first()
    inter_tag = db.query(ContentTag).filter_by(name="Intermediate").first()
    
    contents = [
        {
            "title": "Visual Guide to Basic Algebra",
            "description": "Learn basic algebra through interactive visualizations",
            "content_type": "video",
            "subject": "mathematics",
            "difficulty_level": 1,
            "content_data": {
                "video_url": "https://example.com/videos/algebra-basics",
                "duration": 1200,
                "has_interactive": True
            },
            "visual_affinity": 80.0,
            "auditory_affinity": 40.0,
            "kinesthetic_affinity": 30.0,
            "reading_affinity": 20.0,
            "author": "Dr. Math",
            "tags": [math_tag, beginner_tag] if math_tag and beginner_tag else []
        },
        {
            "title": "Python Programming Workshop",
            "description": "Hands-on programming exercises with Python",
            "content_type": "interactive",
            "subject": "programming",
            "difficulty_level": 2,
            "content_data": {
                "exercises": [
                    {"name": "Variables", "points": 10},
                    {"name": "Functions", "points": 20}
                ],
                "environment": "python-sandbox"
            },
            "visual_affinity": 30.0,
            "auditory_affinity": 20.0,
            "kinesthetic_affinity": 90.0,
            "reading_affinity": 40.0,
            "author": "Code Master",
            "tags": [prog_tag, inter_tag] if prog_tag and inter_tag else []
        },
        {
            "title": "Mathematics Through Stories",
            "description": "Learn math concepts through engaging stories and audio lessons",
            "content_type": "audio",
            "subject": "mathematics",
            "difficulty_level": 1,
            "content_data": {
                "audio_url": "https://example.com/audio/math-stories",
                "duration": 900,
                "transcript_available": True
            },
            "visual_affinity": 20.0,
            "auditory_affinity": 90.0,
            "kinesthetic_affinity": 30.0,
            "reading_affinity": 40.0,
            "author": "Story Math",
            "tags": [math_tag, beginner_tag] if math_tag and beginner_tag else []
        },
        {
            "title": "Programming Fundamentals Reading",
            "description": "Comprehensive text-based guide to programming basics",
            "content_type": "article",
            "subject": "programming",
            "difficulty_level": 1,
            "content_data": {
                "text": "Long article content here...",
                "word_count": 2000,
                "has_examples": True
            },
            "visual_affinity": 30.0,
            "auditory_affinity": 20.0,
            "kinesthetic_affinity": 30.0,
            "reading_affinity": 90.0,
            "author": "Tech Writer",
            "tags": [prog_tag, beginner_tag] if prog_tag and beginner_tag else []
        }
    ]
    
    for content_data in contents:
        # Extract tags before creating content
        tags = content_data.pop("tags", [])
        
        # Check if content already exists
        exists = db.query(LearningContent).filter_by(
            title=content_data["title"]
        ).first()
        
        if not exists:
            content = LearningContent(**content_data)
            content.tags = tags
            db.add(content)
    
    db.commit()
    print("Sample content initialized successfully")

def init_assessment_questions(db: Session) -> None:
    """Initialize default assessment questions"""
    
    questions = [
        {
            "question_text": "I prefer learning through diagrams and visual aids",
            "question_type": "scale",
            "options": {
                "1": "Strongly Disagree",
                "2": "Disagree",
                "3": "Neutral",
                "4": "Agree",
                "5": "Strongly Agree"
            },
            "category": "visual",
            "weight": 1.0,
            "question_metadata": {"type": "preference", "format": "likert"}
        },
        {
            "question_text": "I learn best through listening to lectures and discussions",
            "question_type": "scale",
            "options": {
                "1": "Strongly Disagree",
                "2": "Disagree",
                "3": "Neutral",
                "4": "Agree",
                "5": "Strongly Agree"
            },
            "category": "auditory",
            "weight": 1.0,
            "question_metadata": {"type": "preference", "format": "likert"}
        }
    ]
    
    for question_data in questions:
        # Check if question already exists
        exists = db.query(AssessmentQuestion).filter_by(
            question_text=question_data["question_text"]
        ).first()
        
        if not exists:
            question = AssessmentQuestion(**question_data)
            db.add(question)
    
    db.commit()
    print("Assessment questions initialized successfully")

def init_test_user(db: Session) -> None:
    """Initialize test user for development"""
    test_user = User(
        email="test@example.com",
        hashed_password="$2b$12$test_hash",  # Replace with proper hashed password in production
        full_name="Test User"
    )
    
    # Check if test user already exists
    exists = db.query(User).filter_by(email=test_user.email).first()
    if not exists:
        db.add(test_user)
        db.commit()
        print("Test user created successfully")

def init_data() -> None:
    """Initialize all test data"""
    try:
        db = SessionLocal()
        init_content_tags(db)
        init_sample_content(db)
        init_assessment_questions(db)
        if settings.PROJECT_NAME.lower().endswith("api"):  # Only create test user in development
            init_test_user(db)
        print("Data initialization completed successfully")
    except Exception as e:
        print(f"Error initializing data: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    init_data()