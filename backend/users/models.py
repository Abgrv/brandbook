import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    brandbooks = relationship("Brandbook", back_populates="user")


class Brandbook(Base):
    __tablename__ = "brandbooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="brandbooks")
    sections = relationship("Section", back_populates="brandbook", cascade="all, delete")
    files = relationship("UploadedFile", back_populates="brandbook", cascade="all, delete")


class Section(Base):
    __tablename__ = "sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brandbook_id = Column(UUID(as_uuid=True), ForeignKey("brandbooks.id"))
    type = Column(String, nullable=False)  # e.g. 'logo', 'colors'
    content = Column(JSON, nullable=False)  # flexible data
    order = Column(Integer, default=0)

    brandbook = relationship("Brandbook", back_populates="sections")


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brandbook_id = Column(UUID(as_uuid=True), ForeignKey("brandbooks.id"))
    file_url = Column(String, nullable=False)
    file_type = Column(String)  # 'image', 'pdf', etc.
    label = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    brandbook = relationship("Brandbook", back_populates="files")


# from django.contrib.auth.models import AbstractUser
# from django.db import models
# from rest_framework.exceptions import ValidationError


# class User(AbstractUser):
#     email = models.EmailField(
#         verbose_name='Электронная почта',
#         unique=True,
#         max_length=254
#     )
#     first_name = models.CharField(
#         verbose_name='Имя',
#         max_length=150,
#     )
#     last_name = models.CharField(
#         verbose_name='Фамилия',
#         max_length=150,
#     )

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = (
#         'username',
#         'first_name',
#         'last_name',
#     )

#     class Meta:
#         verbose_name = 'Пользователь'
#         verbose_name_plural = 'Пользователи'
#         constraints = [
#             models.UniqueConstraint(
#                 fields=('username', 'email'),
#                 name='unique_user'
#             )
#         ]

#     def __str__(self):
#         return self.username


# class Follow(models.Model):
#     user = models.ForeignKey(
#         User,
#         related_name='follower',
#         verbose_name='Подписчик',
#         on_delete=models.CASCADE
#     )
#     author = models.ForeignKey(
#         User,
#         related_name='following',
#         verbose_name='Автор',
#         on_delete=models.CASCADE
#     )

#     def __str__(self):
#         return f'Автор: {self.author}, подписчик: {self.user}'

#     def save(self, **kwargs):
#         if self.user == self.author:
#             raise ValidationError("Невозможно подписаться на себя")
#         super().save()

#     class Meta:
#         verbose_name = 'Подписка'
#         verbose_name_plural = 'Подписки'
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['author', 'user'],
#                 name='unique_follower')
#         ]
