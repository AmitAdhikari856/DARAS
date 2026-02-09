from rest_framework import serializers
from assessment.models import DigitalAddictionAssessment

# assessment/serializers.py
from rest_framework import serializers
from assessment.models import DigitalAddictionAssessment

class DigitalAddictionAssessmentSerializer(serializers.ModelSerializer):
    student = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = DigitalAddictionAssessment
        fields = [
            "student",
            "institute",
            "age",
            "gender",
            "da1","da2","da3","da4","da5","da6","da7","da8",
            "primary_device",
            "own_smartphone",
            "mobile_data",
            "screen_weekdays",
            "screen_weekends",
            "night_phone_use",
            "notif_per_hour",
            "social_time",
            "gaming_time",
            "platforms",
            "self_rated_da",
            "predicted_risk",
            "risk_confidence"
        ]
        read_only_fields = ["predicted_risk", "risk_confidence"]


    # ------------------------------
    # FIELD VALIDATIONS
    # ------------------------------
    def validate_age(self, value):
        if value < 15 or value > 45:
            raise serializers.ValidationError("Age must be between 15 and 45.")
        return value

    def validate_gender(self, value):
        if value not in ["Male", "Female"]:
            raise serializers.ValidationError("Gender must be Male or Female.")
        return value

    def validate_da1(self, value): return self.validate_da_field(value)
    def validate_da2(self, value): return self.validate_da_field(value)
    def validate_da3(self, value): return self.validate_da_field(value)
    def validate_da4(self, value): return self.validate_da_field(value)
    def validate_da5(self, value): return self.validate_da_field(value)
    def validate_da6(self, value): return self.validate_da_field(value)
    def validate_da7(self, value): return self.validate_da_field(value)
    def validate_da8(self, value): return self.validate_da_field(value)

    def validate_da_field(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("DA fields must be between 1 and 5.")
        return value

    def validate_primary_device(self, value):
        allowed = ["Smartphone", "Laptop", "Tablet"]
        if value not in allowed:
            raise serializers.ValidationError(f"Primary device must be one of {allowed}.")
        return value

    def validate_own_smartphone(self, value):
        if value not in ["Yes", "No"]:
            raise serializers.ValidationError("Own smartphone must be Yes or No.")
        return value

    def validate_mobile_data(self, value):
        allowed = ["Always", "Sometimes", "Rarely", "No"]
        if value not in allowed:
            raise serializers.ValidationError(f"Mobile data must be one of {allowed}.")
        return value

    def validate_screen_weekdays(self, value):
        allowed = ["<2h","2–3h","3–4h","4–6h",">6h"]
        if value not in allowed:
            raise serializers.ValidationError(f"Weekday screen time must be one of {allowed}.")
        return value

    def validate_screen_weekends(self, value):
        allowed = ["<2h","2–3h","3–4h","4–6h",">6h"]
        if value not in allowed:
            raise serializers.ValidationError(f"Weekend screen time must be one of {allowed}.")
        return value

    def validate_night_phone_use(self, value):
        allowed = ["Never","<30m","30–60m","1–2h",">2h"]
        if value not in allowed:
            raise serializers.ValidationError(f"Night phone use must be one of {allowed}.")
        return value

    def validate_notif_per_hour(self, value):
        allowed = ["<5 times","5–10 times","11–20 times",">20 times"]
        if value not in allowed:
            raise serializers.ValidationError(f"Notifications per hour must be one of {allowed}.")
        return value

    def validate_social_time(self, value):
        allowed = ["<1h","1–2h","2–3h","3–4h",">4h"]
        if value not in allowed:
            raise serializers.ValidationError(f"Social media time must be one of {allowed}.")
        return value

    def validate_gaming_time(self, value):
        allowed = ["None","<30m","30–60m","1–2h",">2h"]
        if value not in allowed:
            raise serializers.ValidationError(f"Gaming time must be one of {allowed}.")
        return value

    def validate_platforms(self, value):
        allowed = {"YouTube","TikTok","Instagram","Facebook","WhatsApp","X/Twitter","Snapchat","Gaming"}
        if not isinstance(value, list):
            raise serializers.ValidationError("Platforms must be a list.")
        invalid = [p for p in value if p not in allowed]
        if invalid:
            raise serializers.ValidationError(f"Invalid platforms: {invalid}")
        return value

    def validate_self_rated_da(self, value):
        allowed = ["not_at_risk","mild","moderate","severe"]
        if value not in allowed:
            raise serializers.ValidationError(f"Self-rated DA must be one of {allowed}.")
        return value

    # --------------------------------------------------
    # CREATE
    # Automatically attach logged-in student
    # --------------------------------------------------
    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["student"] = request.user
        return super().create(validated_data)
