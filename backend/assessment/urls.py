from django.urls import path
from assessment.api.views import (
    PredictAssessmentView,
    DigitalAddictionAssessmentDetailAPI,
)
from assessment.views import assessment_result_page, insights_view

urlpatterns = [
    path("predict/", PredictAssessmentView.as_view(), name="predict-assessment"),
    path(
        "<int:pk>/",
        DigitalAddictionAssessmentDetailAPI.as_view(),
        name="assessment-detail"
    ),


    path("students/assessment_result/<int:pk>/", assessment_result_page, name="assessment-result-page"),

    path('insights/', insights_view, name='insights'),
]



