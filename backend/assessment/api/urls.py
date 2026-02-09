from django.urls import include, path
from .views import PredictAssessmentView

urlpatterns = [
    path('predict/', PredictAssessmentView.as_view(), name='predict-assessment'),
    path('assessment/', include('assessment.urls')),
]
