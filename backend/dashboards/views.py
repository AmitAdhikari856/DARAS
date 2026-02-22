from urllib import request

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from matplotlib.pyplot import plot
from assessment.models import DigitalAddictionAssessment
from assessment.views import create_late_night_pie_chart, create_night_phone_by_age_percentage_bar_chart, create_platform_bar_chart, create_platform_bar_chart_by_gender, create_self_rated_digital_addiction_pie_chart, generate_das_by_age_chart_interactive
from ml.preprocessing import preprocess_assessment 
import numpy as np


# ================================
# STUDENT DASHBOARD
# ================================

from plotly.offline import plot
import plotly.graph_objects as go


def calculate_student_usage_metrics(assessments):
    """
    Calculate average screen, gaming, and social media usage metrics
    based on the provided assessments queryset.
    Returns a dictionary ready for the dashboard summary card.
    """
    # Initialize lists to collect data
    screen_weekdays_list = []
    screen_weekends_list = []
    gaming_time_list = []
    social_media_list = []

    for assessment in assessments:
        numeric_features, _ = preprocess_assessment(assessment, fit=False)
        screen_weekdays_list.append(numeric_features.get("screen_time_weekdays", 0))
        screen_weekends_list.append(numeric_features.get("screen_time_weekends", 0))
        gaming_time_list.append(numeric_features.get("gaming_time", 0))           # in hours
        social_media_list.append(numeric_features.get("social_media_time", 0))     # in hours

    # Compute averages safely
    avg_screen_weekdays = round(np.mean(screen_weekdays_list), 1) if screen_weekdays_list else 0
    avg_screen_weekends = round(np.mean(screen_weekends_list), 1) if screen_weekends_list else 0
    avg_gaming_time_hours = round(np.mean(gaming_time_list), 2) if gaming_time_list else 0
    avg_social_media_time_hours = round(np.mean(social_media_list), 2) if social_media_list else 0

    # Convert hours to minutes for summary cards
    avg_gaming_time_mins = round(avg_gaming_time_hours * 60, 1)
    avg_social_media_time_mins = round(avg_social_media_time_hours * 60, 1)

    return {
        "avg_screen_weekdays": avg_screen_weekdays,
        "avg_screen_weekends": avg_screen_weekends,
        "avg_gaming_time_hours": avg_gaming_time_hours,
        "avg_gaming_time_mins": avg_gaming_time_mins,
        "avg_social_media_time_hours": avg_social_media_time_hours,
        "avg_social_media_time_mins": avg_social_media_time_mins,
        "total_assessments": assessments.count()
    }

def create_student_digital_addiction_trend_line_chart(assessments, max_item_score=5):
    """
    Interactive line chart showing a student's
    digital addiction score trend over time.

    DAS is calculated as the sum of da1 to da8 for each assessment
    and normalized to a 0–100 scale.
    
    Parameters:
    - assessments: list of assessment objects with da1-da8 and created_at
    - max_item_score: maximum value for a single DA item (default 5)
    """

    # Sort assessments chronologically
    assessments = sorted(assessments, key=lambda x: x.created_at)

    dates = []
    scores = []

    max_das = 8 * max_item_score  # maximum possible DAS score

    for assessment in assessments:
        try:
            raw_score = sum(getattr(assessment, f"da{i}", 0) for i in range(1, 9))
            # Normalize to 0-100
            normalized_score = (raw_score / max_das) * 100
        except Exception:
            continue

        date = getattr(assessment, "created_at", None)
        if date is not None:
            dates.append(date.strftime("%Y-%m-%d"))
            scores.append(normalized_score)

    if not scores:
        return "<p><strong>No assessment history available.</strong></p>"

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=scores,
            mode="lines+markers",
            line=dict(width=3, color="royalblue"),
            marker=dict(size=8),
            hovertemplate=(
                "<b>Date:</b> %{x}<br>"
                "<b>Normalized DAS:</b> %{y:.2f}<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title="My Digital Addiction Score Trend (0-100)",
        xaxis_title="Assessment Date",
        yaxis_title="Digital Addiction Score (0-100)",
        template="plotly_white",
        margin=dict(t=60, l=50, r=40, b=50),
        yaxis=dict(range=[0, 100]),
    )

    return plot(fig, output_type="div", include_plotlyjs=False)

# Social media time trend line chart for student dashboard
def create_student_social_time_trend_line_chart(assessments):
    """
    Trend line showing student's social media usage over time.
    Uses categorical social_time mapped to hours and converted to minutes.
    """

    social_map = {
        "<1h": 0.5,
        "1-2h": 1.5,
        "2-3h": 2.5,
        "3-4h": 3.5,
        ">4h": 5
    }

    assessments = sorted(assessments, key=lambda x: x.created_at)

    dates = []
    minutes_used = []

    for assessment in assessments:
        numeric_features, _ = preprocess_assessment(assessment, fit=False)
        date = getattr(assessment, "created_at", None)
        social_time_label = getattr(assessment, "social_time", None)

        if not date or not social_time_label:
            continue

        if social_time_label not in social_map:
            continue

        # Convert hours → minutes
        minutes = social_map[social_time_label] * 60

        dates.append(date.strftime("%Y-%m-%d"))
        minutes_used.append(minutes)

    if not minutes_used:
        return "<p><strong>No social media usage data available.</strong></p>"

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=minutes_used,
            mode="lines+markers",
            line=dict(width=3, color="orange"),
            marker=dict(size=8),
            hovertemplate=(
                "<b>Date:</b> %{x}<br>"
                "<b>Social Media Time:</b> %{y} min<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title="My Social Media Usage Trend",
        xaxis_title="Assessment Date",
        yaxis_title="Social Media Usage in min",
        template="plotly_white",
        margin=dict(t=60, l=50, r=40, b=50),
    )

    return plot(fig, output_type="div", include_plotlyjs=False)



@login_required
def student_dashboard(request):
       # If admin accidentally lands here → redirect
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_dashboard')

    assessments = DigitalAddictionAssessment.objects.filter(
        student=request.user
    ).order_by("created_at")

    addiction_trend_chart = create_student_digital_addiction_trend_line_chart(assessments)
    social_time_trend_chart = create_student_social_time_trend_line_chart(assessments)
    metrics = calculate_student_usage_metrics(assessments)

    context = {
        "addiction_trend_chart": addiction_trend_chart,
        "social_time_trend_chart": social_time_trend_chart,
        "metrics": metrics
    }

    # ✅ IMPORTANT: correct template path
    return render(request, "dashboards/student.html", context)




# ================================
# USE MODEL (ASSESSMENT FORM)
# ================================
@login_required
def use_model(request):
    # Only students should access assessment form
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_dashboard')

    return render(request, 'students/use_model.html')


# ================================
# ABOUT PAGE (STUDENT)
# ================================
@login_required
def about(request):
    return render(request, 'students/about.html')


# ================================
# ADMIN DASHBOARD
# ================================
@login_required
def admin_dashboard(request):
    # Block non-admin users
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('student_dashboard')

    return render(request, 'dashboards/admin.html')


# ================================
# ADMIN – DIGITAL BEHAVIOUR INSIGHTS
# ================================
@login_required
def digital_behaviour_insights(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('student_dashboard')

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
        gaming_time_list.append(numeric_features.get("gaming_time", 0))           # in hours
        social_media_list.append(numeric_features.get("social_media_time", 0))     # in hours

    # Compute averages safely
    avg_screen_weekdays = round(np.mean(screen_weekdays_list), 1) if screen_weekdays_list else 0
    avg_screen_weekends = round(np.mean(screen_weekends_list), 1) if screen_weekends_list else 0
    avg_gaming_time_hours = round(np.mean(gaming_time_list), 2) if gaming_time_list else 0
    avg_social_media_time_hours = round(np.mean(social_media_list), 2) if social_media_list else 0

    # Convert hours to minutes for metric cards
    avg_gaming_time_mins = round(avg_gaming_time_hours * 60, 1)
    avg_social_media_time_mins = round(avg_social_media_time_hours * 60, 1)

    platform_gender_chart = create_platform_bar_chart_by_gender(assessments)
    #self_rated_pie_chart = create_self_rated_digital_addiction_pie_chart(assessments)


    context = {
        "total_assessments": total_assessments,
        "avg_screen_weekdays": avg_screen_weekdays,
        "avg_screen_weekends": avg_screen_weekends,
        "avg_gaming_time": avg_gaming_time_mins,        # now in minutes
        "avg_social_media_time": avg_social_media_time_mins,  # now in minutes

        # Interactive chart div for DAS by age
        "das_chart_div": generate_das_by_age_chart_interactive(assessments),
        # Interactive pie chart for late night phone usage
        "pie_div": create_late_night_pie_chart(assessments),
        # Interactive bar chart for late night phone usage
        "bar_div": create_night_phone_by_age_percentage_bar_chart(assessments),
        # Interactive Bar chart for platform usage
        "platform_bar_div": create_platform_bar_chart(assessments),
        # Interactive Bar chart for platform usage by gender
        "platform_gender_chart": platform_gender_chart,
        # interactive pie chart for self-rated digital addiction levels
        "self_rated_pie_chart_div": create_self_rated_digital_addiction_pie_chart(assessments)
    }

    return render(request, 'admin/insights.html', context)


# ================================
# ADMIN – MODEL METRICS
# ================================
@login_required
def metrics(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('student_dashboard')

    # Placeholder for ML metrics (expand later)
    context = {
        'accuracy': '92%',
        'precision': '90%',
        'recall': '89%',
        'f1_score': '89.5%',
        'model_version': 'v1.0'
    }

    return render(request, 'admin/metrics.html', context)


# ================================
# STUDENT HISTORY
# ================================
@login_required
def assessment_history_view(request):
    assessments = DigitalAddictionAssessment.objects.filter(
        student=request.user
    ).order_by("-created_at")

    return render(
        request,
        "students/history.html",
        {"assessments": assessments}
    )

@login_required
def assessment_detail_view(request, id):
    assessment = get_object_or_404(
        DigitalAddictionAssessment,
        id=id,
        student=request.user   # IMPORTANT: ownership check
    )

    # Compute DAS weighted average
    da_values = [assessment.da1, assessment.da2, assessment.da3, assessment.da4,
                 assessment.da5, assessment.da6, assessment.da7, assessment.da8]
    das_score = sum(da_values) / len(da_values)  # average
    das_score_normalized = (das_score / 5) * 100  # assuming DA1–DA8 are 0–5 Likert scale

    return render(request, 'students/details.html', {
        'assessment': assessment,
        'das_score': round(das_score_normalized, 2),
    })











