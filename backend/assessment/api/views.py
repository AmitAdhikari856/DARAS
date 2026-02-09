from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from assessment.models import DigitalAddictionAssessment
from assessment.api.serializers import DigitalAddictionAssessmentSerializer as AssessmentSerializer

from ml.predictor import predict_risk_with_confidence


class PredictAssessmentView(APIView):
    """
    API endpoint to:
      - Accept user digital behavior input
      - Save it as a DigitalAddictionAssessment instance
      - Run ML prediction
      - Return risk + confidence
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        # Debug incoming data
        print("Incoming data:", request.data)

        serializer = AssessmentSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            # Save instance with the logged-in user as student
            instance = serializer.save(student=request.user)

            # Run prediction
            risk_label, confidence = predict_risk_with_confidence(instance)

            # Save prediction to DB
            instance.predicted_risk = risk_label
            instance.risk_confidence = confidence or 0.0
            instance.save(update_fields=["predicted_risk", "risk_confidence"])

            return Response({
                "id": instance.id,
                "risk": risk_label,
                "confidence": confidence
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DigitalAddictionAssessmentDetailAPI(RetrieveAPIView):
    """
    API endpoint to retrieve a single DigitalAddictionAssessment entry
    along with its predicted risk and confidence.
    """
    queryset = DigitalAddictionAssessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Optionally, restrict retrieval to the logged-in user's assessments
        """
        instance = self.get_object()

        # Optionally enforce that only the student or staff can view
        if instance.student != request.user and not request.user.is_staff:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        data = self.serializer_class(instance).data
        # Include prediction info
        data["predicted_risk"] = instance.predicted_risk
        data["risk_confidence"] = instance.risk_confidence

        return Response(data, status=status.HTTP_200_OK)
