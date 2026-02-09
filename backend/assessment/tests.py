# from django.test import TestCase
# from django.contrib.auth import get_user_model
# from .models import DigitalAddictionAssessment


# User = get_user_model()


# class AssessmentModelTest(TestCase):

#     def test_create_assessment(self):
#         user = User.objects.create_user(
#             username="student1",
#             password="test123"
#         )

#         assessment = DigitalAddictionAssessment.objects.create(
#             student=user,
#             institute="Test College",
#             age=20,
#             gender="Male",
#             da1=1, da2=1, da3=1, da4=1,
#             da5=1, da6=1, da7=1, da8=1,
#             primary_device="Mobile",
#             own_smartphone="Yes",
#             mobile_data="Yes",
#             screen_weekdays="2-4",
#             screen_weekends="4-6",
#             night_phone_use="Yes",
#             notif_per_hour="10+",
#             social_time="2-3",
#             gaming_time="1-2",
#             platforms=["Facebook"],
#             self_rated_da="Moderate",
#             predicted_risk="Low"
#         )

#         self.assertEqual(assessment.student.username, "student1")
