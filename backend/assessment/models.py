from django.db import models
from django.conf import settings


class DigitalAddictionAssessment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    # Demographics
    institute = models.CharField(max_length=255)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10)

    # Compulsive behaviour (DA1–DA8)
    da1 = models.IntegerField()
    da2 = models.IntegerField()
    da3 = models.IntegerField()
    da4 = models.IntegerField()
    da5 = models.IntegerField()
    da6 = models.IntegerField()
    da7 = models.IntegerField()
    da8 = models.IntegerField()

    # Digital usage
    primary_device = models.CharField(max_length=20)
    own_smartphone = models.CharField(max_length=5)
    mobile_data = models.CharField(max_length=20)
    screen_weekdays = models.CharField(max_length=10)
    screen_weekends = models.CharField(max_length=10)
    night_phone_use = models.CharField(max_length=10)
    notif_per_hour = models.CharField(max_length=20)
    social_time = models.CharField(max_length=10)
    gaming_time = models.CharField(max_length=10)

    platforms = models.JSONField()

    # Self-rated
    self_rated_da = models.CharField(max_length=20)

    # ML Output
    predicted_risk = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
