from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from .serializers import RegisterSerializer, UserSerializer, PatientSerializer, DoctorSerializer, MappingSerializer
from .models import User, Patient, Doctor, Mapping


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data.copy()

        if "username" not in data or not data["username"]:
            data["username"] = data.get("email").split("@")[0]

        if not request.user.is_authenticated or not request.user.is_superuser:
            data["is_staff"] = False
            data["is_superuser"] = False

        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail":"Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.check_password(password):
            return Response({"detail":"Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
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
        if self.request.user.is_superuser or self.request.user.is_staff:
            return Patient.objects.all().order_by("-created_at")
        return Patient.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return Patient.objects.all()
        return Patient.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        patient = self.get_object()
        if not (request.user.is_superuser or request.user.is_staff) and patient.user != request.user:
            return Response({"detail": "Not authorized to delete this patient."}, status=403)
        return super().destroy(request, *args, **kwargs)

class DoctorListCreateView(generics.ListCreateAPIView):
    serializer_class = DoctorSerializer
    queryset = Doctor.objects.all().order_by("-created_at")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DoctorSerializer
    queryset = Doctor.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            return Response({"detail": "Only admin/staff can delete doctors."}, status=403)
        return super().destroy(request, *args, **kwargs)

class MappingListCreateView(generics.ListCreateAPIView):
    serializer_class = MappingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return Mapping.objects.all().order_by("-created_at")
        return Mapping.objects.filter(patient__user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        patient = serializer.validated_data.get("patient")
        if not (self.request.user.is_superuser or self.request.user.is_staff) and patient.user != self.request.user:
            raise permissions.PermissionDenied("Cannot assign doctor to another user's patient.")
        serializer.save(assigned_by=self.request.user)

class MappingDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = MappingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return Mapping.objects.all()
        return Mapping.objects.filter(patient__user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        mapping = self.get_object()
        if not (request.user.is_superuser or request.user.is_staff) and mapping.patient.user != request.user:
            return Response({"detail": "Not authorized to delete this mapping."}, status=403)
        return super().destroy(request, *args, **kwargs)

class DoctorsForPatientView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, patient_id):
        if request.user.is_superuser or request.user.is_staff:
            patient = get_object_or_404(Patient, id=patient_id)
        else:
            patient = get_object_or_404(Patient, id=patient_id, user=request.user)

        mappings = Mapping.objects.filter(patient=patient).select_related("doctor")
        doctors = [{"id": m.doctor.id, "name": m.doctor.name, "specialty": m.doctor.specialty, "phone": m.doctor.phone} for m in mappings]
        return Response({"patient": {"id": patient.id, "name": patient.name}, "doctors": doctors})


