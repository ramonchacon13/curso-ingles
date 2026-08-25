from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Boolean, Text, ForeignKey, DateTime, JSON, Float, UniqueConstraint
)
from sqlalchemy.orm import relationship

from database import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    nombre = Column(String(120), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    nivel = Column(String(8), default="A1")
    is_premium = Column(Boolean, default=False)
    plan = Column(String(20), default="free")
    role = Column(String(20), default="user")
    email_opt_in = Column(Boolean, default=True)
    avatar_kind = Column(String(20), default="initials")
    avatar_value = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    results = relationship("TestResult", back_populates="user", cascade="all, delete-orphan")


class Level(Base):
    __tablename__ = "niveles"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(8), unique=True, nullable=False)
    name = Column(String(80), nullable=False)
    description = Column(Text)
    orden = Column(Integer, default=0)

    courses = relationship("Course", back_populates="level", cascade="all, delete-orphan")
    tests = relationship("Test", back_populates="level", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "cursos"

    id = Column(Integer, primary_key=True, index=True)
    level_id = Column(Integer, ForeignKey("niveles.id"), nullable=False)
    title = Column(String(160), nullable=False)
    description = Column(Text)
    orden = Column(Integer, default=0)

    level = relationship("Level", back_populates="courses")
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")


class Lesson(Base):
    __tablename__ = "lecciones"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("cursos.id"), nullable=False)
    title = Column(String(160), nullable=False)
    content = Column(Text)
    orden = Column(Integer, default=0)
    is_premium = Column(Boolean, default=False)

    course = relationship("Course", back_populates="lessons")


class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    level_id = Column(Integer, ForeignKey("niveles.id"), nullable=False)
    title = Column(String(160), nullable=False)

    level = relationship("Level", back_populates="tests")
    questions = relationship("Question", back_populates="test", cascade="all, delete-orphan")
    results = relationship("TestResult", back_populates="test", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "preguntas"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    correct = Column(Integer, nullable=False)
    explanation = Column(Text)

    test = relationship("Test", back_populates="questions")


class TestResult(Base):
    __tablename__ = "resultados_test"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    score = Column(Integer, default=0)
    total = Column(Integer, default=0)
    completed_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="results")
    test = relationship("Test", back_populates="results")


class ChatMessage(Base):
    __tablename__ = "chat_mensajes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    sender_name = Column(String(120), nullable=True)
    role = Column(String(20), nullable=False, default="user")
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="messages")


class PrivateMessage(Base):
    __tablename__ = "mensajes_privados"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    peer_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    sender_name = Column(String(120), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow)


class Progreso(Base):
    __tablename__ = "progreso"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lecciones.id"), nullable=False)
    completed_at = Column(DateTime, default=utcnow)

    __table_args__ = (
        __import__("sqlalchemy").UniqueConstraint("user_id", "lesson_id", name="uq_progreso"),
    )
