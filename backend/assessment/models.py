from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class DigitalAddictionAssessment(models.Model):
    # User
    student = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="assessments")

    
    # Demographics
    institute = models.CharField(max_length=255)
    age = models.PositiveIntegerField()
    
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    # Digital Addiction Compulsive Behaviours (DA1 - DA8)
    da1 = models.PositiveSmallIntegerField()
    da2 = models.PositiveSmallIntegerField()
    da3 = models.PositiveSmallIntegerField()
    da4 = models.PositiveSmallIntegerField()
    da5 = models.PositiveSmallIntegerField()
    da6 = models.PositiveSmallIntegerField()
    da7 = models.PositiveSmallIntegerField()
    da8 = models.PositiveSmallIntegerField()

    # Digital Usage Behaviours
    DEVICE_CHOICES = [
        ('Smartphone', 'Smartphone'),
        ('Laptop', 'Laptop'),
        ('Tablet', 'Tablet'),
    ]
    primary_device = models.CharField(max_length=20, choices=DEVICE_CHOICES)
    
    YES_NO_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    own_smartphone = models.CharField(max_length=3, choices=YES_NO_CHOICES)
    
    MOBILE_DATA_CHOICES = [
        ('Always', 'Always'),
        ('Sometimes', 'Sometimes'),
        ('Rarely', 'Rarely'),
        ('No', 'No'),
    ]
    mobile_data = models.CharField(max_length=10, choices=MOBILE_DATA_CHOICES)

    SCREEN_TIME_CHOICES = [
        ('<2h', '<2h'),
        ('2–3h', '2–3h'),
        ('3–4h', '3–4h'),
        ('4–6h', '4–6h'),
        ('>6h', '>6h'),
    ]
    screen_weekdays = models.CharField(max_length=10, choices=SCREEN_TIME_CHOICES)
    screen_weekends = models.CharField(max_length=10, choices=SCREEN_TIME_CHOICES)

    NIGHT_PHONE_USE_CHOICES = [
        ('Never', 'Never'),
        ('<30m', '<30m'),
        ('30–60m', '30–60m'),
        ('1–2h', '1–2h'),
        ('>2h', '>2h'),
    ]
    night_phone_use = models.CharField(max_length=10, choices=NIGHT_PHONE_USE_CHOICES)

    NOTIF_CHOICES = [
        ('<5 times', '<5 times'),
        ('5–10 times', '5–10 times'),
        ('11–20 times', '11–20 times'),
        ('>20 times', '>20 times'),
    ]
    notif_per_hour = models.CharField(max_length=15, choices=NOTIF_CHOICES)

    SOCIAL_TIME_CHOICES = [
        ('<1h', '<1h'),
        ('1–2h', '1–2h'),
        ('2–3h', '2–3h'),
        ('3–4h', '3–4h'),
        ('>4h', '>4h'),
    ]
    social_time = models.CharField(max_length=10, choices=SOCIAL_TIME_CHOICES)

    GAMING_TIME_CHOICES = [
        ('None', 'None'),
        ('<30m', '<30m'),
        ('30–60m', '30–60m'),
        ('1–2h', '1–2h'),
        ('>2h', '>2h'),
    ]
    gaming_time = models.CharField(max_length=10, choices=GAMING_TIME_CHOICES)

    # Platforms used regularly (multi-select)
    platforms = models.JSONField(default=list, blank=True)  # stores a list of selected platforms

    # Self Rated Digital Addiction
    SELF_RATED_CHOICES = [
        ('not_at_risk', 'Not at risk'),
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
    ]
    self_rated_da = models.CharField(max_length=20, choices=SELF_RATED_CHOICES)

    # Predicted Risk
    predicted_risk = models.CharField(max_length=20, choices=SELF_RATED_CHOICES, null=True, blank=True)
    risk_confidence = models.FloatField(null=True, blank=True)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.username} - {self.created_at.date()}"

