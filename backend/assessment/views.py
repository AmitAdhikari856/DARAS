# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required

# from assessment.forms import AssessmentForm
# from assessment.models import DigitalAddictionAssessment
# from ml.predictor import predict_risk_with_confidence

# # -----------------------
# # Take Assessment Page
# # -----------------------
# @login_required
# def take_assessment(request):
#     """
#     Renders the assessment form and saves the submission.
#     Runs ML prediction on save and stores risk + confidence.
#     """

#     # Optional: prevent resubmission (or allow multiple entries)
#     if request.user.digitaladdictionassessment_set.exists():
#         # Redirect to latest result or a success page
#         latest_assessment = request.user.digitaladdictionassessment_set.latest('created_at')
#         return redirect('assessment_result', assessment_id=latest_assessment.id)

#     if request.method == "POST":
#         form = AssessmentForm(request.POST)
#         if form.is_valid():
#             assessment = form.save(commit=False)
#             assessment.student = request.user
#             assessment.save()

#             # 🔥 ML Prediction
#             risk, confidence = predict_risk_with_confidence(instance=assessment)

#             # Update DB
#             DigitalAddictionAssessment.objects.filter(id=assessment.id).update(
#                 predicted_risk=risk,
#                 risk_confidence=confidence
#             )

#             return redirect('assessment_result', assessment_id=assessment.id)

#     else:
#         form = AssessmentForm()

#     return render(
#         request,
#         "students/use_model.html",
#         {"form": form}
#     )


# # -----------------------
# # Assessment Result Page
# # -----------------------
# @login_required
# def assessment_result(request, assessment_id):
#     """
#     Shows the result of a specific assessment.
#     """
#     assessment = get_object_or_404(DigitalAddictionAssessment, id=assessment_id)
#     return render(
#         request,
#         "students/assessment_result.html",
#         {"assessment": assessment}
#     )
