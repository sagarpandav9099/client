from django.urls import path
from .views import (
    register_view, 
    login_view, 
    logout_view, 
    exam_list_view, 
    take_exam_view,
    exam_results_view
)

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('exam-list/', exam_list_view, name='exam_list'),
    path('exam/<int:exam_id>/', take_exam_view, name='take_exam'),
    path('exam-results/', exam_results_view, name='exam_results'),
]