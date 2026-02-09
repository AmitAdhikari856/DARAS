from django.urls import path, include
from . import views
from .api.views import DigitalAddictionAssessmentDetailAPI, PredictAssessmentView

urlpatterns = [
    
    #path('use-model/', views.use_model, name='use-model'),  # Form page
    path('predict/', PredictAssessmentView.as_view(), name='assessment-predict'),  # API endpoint for prediction
    path('<int:pk>/', DigitalAddictionAssessmentDetailAPI.as_view(), name='assessment-detail'),  # API endpoint for retrieving assessment details
    

]
