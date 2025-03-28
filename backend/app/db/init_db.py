from sqlalchemy.orm import Session
import os
# 确保导入顺序正确
from app.models.user import User
from app.models.learning_assessment import AssessmentQuestion, LearningStyleAssessment, UserResponse
from app.models.content import LearningContent, ContentTag, UserContentInteraction
from app.models.content_interaction import ContentInteraction
from app.models.learning_path import LearningPath, PathEnrollment
from app.core.config import settings
from app.db.session import SessionLocal
from app.db.session import Base, engine

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
        },
        {
            "question_text": "I learn best by doing hands-on activities",
            "question_type": "scale",
            "options": {
                "1": "Strongly Disagree",
                "2": "Disagree",
                "3": "Neutral",
                "4": "Agree",
                "5": "Strongly Agree"
            },
            "category": "kinesthetic",
            "weight": 1.0,
            "question_metadata": {"type": "preference", "format": "likert"}
        },
        {
            "question_text": "I prefer reading texts and written instructions",
            "question_type": "scale",
            "options": {
                "1": "Strongly Disagree",
                "2": "Disagree",
                "3": "Neutral",
                "4": "Agree",
                "5": "Strongly Agree"
            },
            "category": "reading",
            "weight": 1.0,
            "question_metadata": {"type": "preference", "format": "likert"}
        }
    ]
    
    try:
        # 检查是否已存在评估问题
        existing_questions = db.query(AssessmentQuestion).all()
        if existing_questions:
            print(f"已有 {len(existing_questions)} 个评估问题，跳过初始化")
            return
            
        # 添加新问题
        for i, question_data in enumerate(questions, 1):
            # 确保问题ID与测试脚本中使用的ID一致
            db_question = AssessmentQuestion(**question_data)
            db.add(db_question)
            
        db.commit()
        print("评估问题初始化成功")
        
        # 验证问题是否已创建
        created_questions = db.query(AssessmentQuestion).all()
        print(f"已创建 {len(created_questions)} 个评估问题:")
        for q in created_questions:
            print(f"  - ID {q.id}: {q.category} ({q.question_text[:30]}...)")
            
    except Exception as e:
        db.rollback()
        print(f"Error initializing assessment questions: {e}")
        raise

def init_test_user(db: Session) -> None:
    """Initialize test user for development"""
    try:
        test_user = {
            "email": "test@example.com",
            "hashed_password": "$2b$12$test_hash",  # Replace with proper hashed password
            "full_name": "Test User"
        }
        
        user = User(**test_user)
        db.add(user)
        db.commit()
        print("Test user created successfully")
    except Exception as e:
        db.rollback()
        print(f"Error creating test user: {e}")
        raise

def reset_db() -> None:
    """Reset database by removing and recreating it"""
    if settings.SQLALCHEMY_DATABASE_URI.startswith('sqlite:///'):
        db_path = settings.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
        if os.path.exists(db_path):
            try:
                # Close all connections first
                engine.dispose()
                os.remove(db_path)
                print(f"Database file {db_path} removed successfully")
            except Exception as e:
                print(f"Error removing database file: {e}")
                raise

def create_tables() -> None:
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise

def init_db(db: Session = None) -> None:
    """Initialize database with default data"""
    try:
        # Reset database
        reset_db()
        
        # Create new tables
        create_tables()
        
        # Create new database session if not provided
        if db is None:
            db = SessionLocal()
        
        try:
            # Initialize test data
            init_test_user(db)
            init_assessment_questions(db)
            
            print("Database initialized successfully")
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error during database initialization: {e}")
        raise

if __name__ == "__main__":
    init_db()