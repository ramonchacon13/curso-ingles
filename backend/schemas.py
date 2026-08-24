from pydantic import BaseModel, EmailStr
from typing import Optional, List


class UserCreate(BaseModel):
    email: str
    nombre: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    nombre: str
    nivel: str
    is_premium: bool
    plan: str
    role: str = "user"
    email_opt_in: bool = True

    class Config:
        from_attributes = True


class LevelOut(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str]
    orden: int

    class Config:
        from_attributes = True


class LessonOut(BaseModel):
    id: int
    course_id: int
    title: str
    content: Optional[str]
    orden: int
    is_premium: bool
    level_code: Optional[str] = None

    class Config:
        from_attributes = True


class CourseOut(BaseModel):
    id: int
    level_id: int
    title: str
    description: Optional[str]
    orden: int
    lessons: List[LessonOut] = []

    class Config:
        from_attributes = True


class QuestionOut(BaseModel):
    id: int
    prompt: str
    options: List[str]
    correct: int
    explanation: Optional[str]

    class Config:
        from_attributes = True


class TestOut(BaseModel):
    id: int
    level_id: int
    title: str
    questions: List[QuestionOut] = []

    class Config:
        from_attributes = True


class TestSubmit(BaseModel):
    test_id: int
    answers: List[int]


class TestResultOut(BaseModel):
    test_id: int
    score: int
    total: int
    completed_at: str
    nivel_actualizado: bool = False
    nivel: Optional[str] = None

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
