from django.urls import path

from core.views import (
    RegisterView, LoginView,
    PatientListCreateView, PatientDetailView,
    DoctorListCreateView, DoctorDetailView,
    MappingListCreateView, MappingDetailView, DoctorsForPatientView
)
from django.http import JsonResponse

def root(request):
    return JsonResponse({"message": "Healthcare API is running"})

urlpatterns = [
    path("", root),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/login/", LoginView.as_view(), name="login"),
    path("api/patients/", PatientListCreateView.as_view(), name="patients_list_create"),
    path("api/patients/<int:pk>/", PatientDetailView.as_view(), name="patients_detail"),
    path("api/doctors/", DoctorListCreateView.as_view(), name="doctors_list_create"),
    path("api/doctors/<int:pk>/", DoctorDetailView.as_view(), name="doctors_detail"),
    path("api/mappings/", MappingListCreateView.as_view(), name="mappings_list_create"),
    path("api/mappings/<int:pk>/", MappingDetailView.as_view(), name="mappings_detail"),
    path("api/mappings/<int:patient_id>/doctors/", DoctorsForPatientView.as_view(), name="doctors_for_patient"),
]
