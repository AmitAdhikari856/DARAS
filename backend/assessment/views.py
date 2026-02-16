from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from assessment.models import DigitalAddictionAssessment

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from assessment.models import DigitalAddictionAssessment
from ml.preprocessing import preprocess_assessment# your preprocessing function
import numpy as np
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from assessment.models import DigitalAddictionAssessment
from ml.preprocessing import preprocess_assessment
import numpy as np


@login_required
def assessment_result_page(request, pk):
    assessment = get_object_or_404(
        DigitalAddictionAssessment,
        pk=pk,
        student=request.user
    )

    return render(
        request,
        "students/assessment_result.html",
        {"assessment": assessment}
    )

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from assessment.models import DigitalAddictionAssessment
from ml.preprocessing import preprocess_assessment
import numpy as np

@login_required
def insights_view(request):
    assessments = DigitalAddictionAssessment.objects.all()
    total_assessments = assessments.count()

    screen_weekdays_list = []
    screen_weekends_list = []
    gaming_time_list = []
    social_media_list = []

    for assessment in assessments:
        # Preprocess assessment; returns (numeric_features, encoders)
        numeric_features, _ = preprocess_assessment(assessment, fit=False)

        # Access numeric values by column name
        screen_weekdays_list.append(numeric_features["screen_time_weekdays"])
        screen_weekends_list.append(numeric_features["screen_time_weekends"])
        gaming_time_list.append(numeric_features.get("gaming_time", 0))
        social_media_list.append(numeric_features.get("social_media_time", 0))

    # Compute averages safely
    avg_screen_weekdays = round(np.mean(screen_weekdays_list), 1) if screen_weekdays_list else 0
    avg_screen_weekends = round(np.mean(screen_weekends_list), 1) if screen_weekends_list else 0
    avg_gaming_time = round(np.mean(gaming_time_list), 0) if gaming_time_list else 0
    avg_social_media_time = round(np.mean(social_media_list), 0) if social_media_list else 0

    context = {
        "total_assessments": total_assessments,
        "avg_screen_weekdays": avg_screen_weekdays,
        "avg_screen_weekends": avg_screen_weekends,
        "avg_gaming_time": avg_gaming_time,
        "avg_social_media_time": avg_social_media_time,
    }

    return render(request, "admin/insights.html", context)




