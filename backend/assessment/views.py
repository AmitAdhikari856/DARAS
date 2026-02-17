import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings

from assessment.models import DigitalAddictionAssessment
from ml.preprocessing import preprocess_assessment

import plotly.graph_objects as go
from plotly.offline import plot


@login_required
def assessment_result_page(request, pk):
    # Only allow the logged-in user to access their assessment
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



def generate_das_by_age_chart_interactive(assessments):
    """
    Generates an interactive Plotly bar chart of average DAS (0-100%)
    across age groups, showing the number of assessments per group.
    
    Returns HTML div string to embed in the template.
    """

    # Custom age groups
    age_groups = {
        "15-20": [],
        "21-25": [],
        "26-30": [],
        "31-35": [],
        "36-40": [],
        "41-45": [],
        "46+": [],
    }

    # Normalization parameters for DAS
    min_score, max_score = 1, 5  # 1–5 scale

    for assessment in assessments:
        numeric_features, _ = preprocess_assessment(assessment, fit=False)
        age = numeric_features.get("age")
        das = numeric_features.get("DAS_weighted", 0)

        # Convert Series / NumPy types to scalar
        if hasattr(age, "item"):
            age = age.item()
        if hasattr(das, "item"):
            das = das.item()

        if age is None:
            continue

        try:
            age = int(age)
            das = float(das)
        except (ValueError, TypeError):
            continue

        # Normalize DAS to 0-100%
        das_normalized = ((das - min_score) / (max_score - min_score)) * 100
        das_normalized = min(max(das_normalized, 0), 100)

        # Assign to age group
        if 15 <= age <= 20:
            age_groups["15-20"].append(das_normalized)
        elif 21 <= age <= 25:
            age_groups["21-25"].append(das_normalized)
        elif 26 <= age <= 30:
            age_groups["26-30"].append(das_normalized)
        elif 31 <= age <= 35:
            age_groups["31-35"].append(das_normalized)
        elif 36 <= age <= 40:
            age_groups["36-40"].append(das_normalized)
        elif 41 <= age <= 45:
            age_groups["41-45"].append(das_normalized)
        else:
            age_groups["46+"].append(das_normalized)

    # Compute averages and counts
    labels = list(age_groups.keys())
    avg_scores = [round(np.mean(values), 1) if values else 0 for values in age_groups.values()]
    counts = [len(values) for values in age_groups.values()]

    # Create interactive bar chart
    fig = go.Figure(
        data=go.Bar(
            x=labels,
            y=avg_scores,
            text=[f"{score} ({count})" for score, count in zip(avg_scores, counts)],
            textposition='auto',
            marker_color='#4a90e2',
            hovertemplate=
                'Age Group: %{x}<br>'+
                'Average DAS: %{y:.1f}%<br>'+
                'Number of assessments: %{text}<extra></extra>'
        )
    )

    fig.update_layout(
        title="Average Digital Addiction Score by Age Group (%)",
        xaxis_title="Age Group",
        yaxis_title="DAS (Normalized 0–100%)",
        yaxis=dict(range=[0, 100]),
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40)
    )

    # Return HTML div string
    chart_div = plot(fig, output_type='div', include_plotlyjs=False)
    return chart_div


@login_required
def insights_view(request):
    # Fetch all assessments
    assessments = DigitalAddictionAssessment.objects.all()
    total_assessments = assessments.count()

    screen_weekdays_list = []
    screen_weekends_list = []
    gaming_time_list = []
    social_media_list = []

    for assessment in assessments:
        numeric_features, _ = preprocess_assessment(assessment, fit=False)
        screen_weekdays_list.append(numeric_features.get("screen_time_weekdays", 0))
        screen_weekends_list.append(numeric_features.get("screen_time_weekends", 0))
        gaming_time_list.append(numeric_features.get("gaming_time", 0))
        social_media_list.append(numeric_features.get("social_media_time", 0))

    # Compute averages safely
    avg_screen_weekdays = round(np.mean(screen_weekdays_list), 1) if screen_weekdays_list else 0
    avg_screen_weekends = round(np.mean(screen_weekends_list), 1) if screen_weekends_list else 0
    avg_gaming_time = round(np.mean(gaming_time_list), 0) if gaming_time_list else 0
    avg_social_media_time = round(np.mean(social_media_list), 0) if social_media_list else 0

    # # Generate DAS chart for all assessments
    # das_chart_url = generate_das_by_age_chart_interactive(assessments)

    context = {
        "total_assessments": total_assessments,
        "avg_screen_weekdays": avg_screen_weekdays,
        "avg_screen_weekends": avg_screen_weekends,
        "avg_gaming_time": avg_gaming_time,
        "avg_social_media_time": avg_social_media_time,
        # Interactive chart div
        "das_chart_div": generate_das_by_age_chart_interactive(assessments),
    }

    return render(request, "admin/insights.html", context)
