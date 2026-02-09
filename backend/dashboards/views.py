from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from assessment.models import DigitalAddictionAssessment 


# ================================
# STUDENT DASHBOARD
# ================================
@login_required
def student_dashboard(request):
    # If admin accidentally lands here → redirect
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_dashboard')

    return render(request, 'dashboards/student.html')


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

    # Example insights data (can be expanded later)
    total_assessments = DigitalAddictionAssessment.objects.count()
    high_risk = DigitalAddictionAssessment.objects.filter(predicted_risk='High').count()
    medium_risk = DigitalAddictionAssessment.objects.filter(predicted_risk='Medium').count()
    low_risk = DigitalAddictionAssessment.objects.filter(predicted_risk='Low').count()

    context = {
        'total_assessments': total_assessments,
        'high_risk': high_risk,
        'medium_risk': medium_risk,
        'low_risk': low_risk,
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


# # ================================
# # STUDENT HISTORY
# # ================================
# @login_required
# def student_history(request):
#     # Admins should not access student history page
#     if request.user.is_staff or request.user.is_superuser:
#         return redirect('admin_dashboard')

#     history = DigitalAddictionAssessment.objects.filter(
#         participant_name=request.user.username
#     ).order_by('-created_at')

#     return render(
#         request,
#         'students/student_history.html',
#         {'history': history}
#     )











