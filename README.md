# Django Healthcare Project

A Django-based backend project for managing healthcare data including users, patients, doctors, and doctor-patient mappings. The project includes JWT authentication for secure access and role-based permissions for staff/admin users.

---

## Features

- **User Authentication**: JWT-based login and registration  
- **Admin & Staff Users**: Can manage all patients, doctors, and mappings  
- **Patients Management**: CRUD operations for patients  
- **Doctors Management**: CRUD operations for doctors (admin/staff only)  
- **Mappings**: Assign doctors to patients with permission checks  
- **Role-Based Permissions**: Normal users can only access their own data  
- **Secure Passwords**: Passwords are hashed and stored securely  

---

## Project Structure

# Django Healthcare Project

A Django-based backend project for managing healthcare data including users, patients, doctors, and doctor-patient mappings. The project includes JWT authentication for secure access and role-based permissions for staff/admin users.

---

## Features

- **User Authentication**: JWT-based login and registration  
- **Admin & Staff Users**: Can manage all patients, doctors, and mappings  
- **Patients Management**: CRUD operations for patients  
- **Doctors Management**: CRUD operations for doctors (admin/staff only)  
- **Mappings**: Assign doctors to patients with permission checks  
- **Role-Based Permissions**: Normal users can only access their own data  
- **Secure Passwords**: Passwords are hashed and stored securely  

---

## Project Structure


---

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Gnaneshwar25/django-healthcare.git
cd django-healthcare
conda create -n DjangoHC python=3.10
conda activate DjangoHC

pip install -r requirements.txt

DB_NAME=myproject_db
DB_USER=root
DB_PASSWORD=yourpassword
DB_HOST=127.0.0.1
DB_PORT=3306
SECRET_KEY=your-django-secret-key

python manage.py makemigrations
python manage.py migrate

python manage.py createsuperuser

python manage.py runserver

API Endpoints

Authentication

POST /api/auth/register/ - Register a new user

POST /api/auth/login/ - Login and receive JWT tokens

Patients

GET /api/patients/ - List patients

POST /api/patients/ - Create patient

GET /api/patients/<id>/ - Retrieve patient

PUT /api/patients/<id>/ - Update patient

DELETE /api/patients/<id>/ - Delete patient

Doctors

GET /api/doctors/ - List doctors

POST /api/doctors/ - Create doctor

GET /api/doctors/<id>/ - Retrieve doctor

PUT /api/doctors/<id>/ - Update doctor

DELETE /api/doctors/<id>/ - Delete doctor (admin/staff only)

Mappings

GET /api/mappings/ - List doctor-patient mappings

POST /api/mappings/ - Create mapping

GET /api/mappings/<id>/ - Retrieve mapping

DELETE /api/mappings/<id>/ - Delete mapping

*Notes

The first registered user automatically becomes a superuser/admin.

Normal users can only manage their own patients and mappings.

All API requests require authentication via JWT tokens except for registration and login.

Author

Shakapuram Gnaneshwar
Email: gnaneshwar2321@gmail.com
