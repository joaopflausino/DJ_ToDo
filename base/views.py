# views.py
from django.shortcuts import render
from .views_files.login_views import CustomLoginView
from .views_files.registration_views import RegisterPage
from .views_files.task_views import (
    TaskList,
    TaskDetail,
    TaskCreate,
    TaskUpdate,
    DeleteView,
    TaskReorder,
)
