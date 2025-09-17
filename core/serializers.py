from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import serializers, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from rest_framework.validators import UniqueValidator

from .models import Patient, Doctor, Mapping

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "name", "email", "password")

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already in use.")
        return value

    def create(self, validated_data):
        name = validated_data.pop("name")
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        user = User(username=email, email=email)
        user.set_password(password)
        user.first_name = name
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name")


class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Patient
        fields = ("id", "name", "age", "gender", "address", "user", "created_at")
        read_only_fields = ("id", "user", "created_at")


class DoctorSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=Doctor.objects.all())]
    )

    class Meta:
        model = Doctor
        fields = ("id", "name", "email", "specialty", "phone", "created_at")
        read_only_fields = ("id", "created_at")


class MappingSerializer(serializers.ModelSerializer):
    assigned_by = UserSerializer(read_only=True)

    class Meta:
        model = Mapping
        fields = ["id", "patient", "doctor", "assigned_by", "created_at"]
        read_only_fields = ("id", "assigned_by", "created_at")

    def validate(self, attrs):
        request = self.context.get("request")
        patient = attrs.get("patient")
        if patient and request and patient.user != request.user:
            raise serializers.ValidationError("You can only assign doctors to patients you created.")
        return attrs

    def create(self, validated_data):
        validated_data["assigned_by"] = self.context["request"].user
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError("This patient-doctor mapping already exists.")


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"id": user.id, "email": user.email}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        if not email or not password:
            return Response({"detail": "email and password required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {"id": user.id, "email": user.email, "name": user.first_name}
        })


class PatientListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Patient.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Patient.objects.filter(user=self.request.user)


class DoctorListCreateView(generics.ListCreateAPIView):
    serializer_class = DoctorSerializer
    queryset = Doctor.objects.all().order_by("-created_at")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DoctorSerializer
    queryset = Doctor.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class MappingListCreateView(generics.ListCreateAPIView):
    serializer_class = MappingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Mapping.objects.filter(patient__user=self.request.user).order_by("-assigned_at")

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)


class MappingDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = MappingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Mapping.objects.filter(patient__user=self.request.user)


class DoctorsForPatientView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, patient_id):
        patient = get_object_or_404(Patient, id=patient_id, user=request.user)
        mappings = Mapping.objects.filter(patient=patient).select_related("doctor")
        doctors = [{"id": m.doctor.id, "name": m.doctor.name, "email": m.doctor.email,
                    "specialty": m.doctor.specialty, "phone": m.doctor.phone} for m in mappings]
        return Response({"patient": {"id": patient.id, "name": patient.name}, "doctors": doctors})

