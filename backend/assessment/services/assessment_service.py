# from assessment.models import DigitalAddictionAssessment
# from ml.predictor import predict_risk


# def create_assessment(student, validated_data):

#     assessment = DigitalAddictionAssessment.objects.create(
#         student=student,
#         **validated_data
#     )

#     # ML inference
#     assessment.predicted_risk = predict_risk(assessment)
#     assessment.save()

#     return assessment
