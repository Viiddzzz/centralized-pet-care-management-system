# 🐾 Centralized Pet Care Management System

A full-stack web application developed using **Python, Flask, HTML, CSS, JavaScript, and MongoDB** to simplify pet care management. The system provides separate portals for **users** and **administrators**, allowing users to book veterinary appointments, browse doctors, purchase pet accessories, and manage pet information, while administrators oversee appointments, doctors, and system data.

---

# 📘 Project Overview

The Centralized Pet Care Management System is designed to provide a single platform for managing essential pet care services. Pet owners can register, maintain pet profiles, book veterinary appointments, explore available doctors, and shop for pet accessories.

The application implements **role-based authentication**, where users and administrators have separate dashboards with different functionalities. Appointment requests are reviewed by the administrator before confirmation, ensuring an organized and efficient workflow.

---

# 🎯 Objectives

- Simplify veterinary appointment booking.
- Provide secure role-based access for users and administrators.
- Maintain centralized pet and doctor information.
- Enable pet owners to browse and purchase accessories.
- Improve the management of veterinary services through a web application.

---

# 🧩 Features

- 🔐 Role-Based Authentication (Admin & User)
- 👤 User Registration and Secure Login
- 🐾 Pet Profile Management
- 📅 Veterinary Appointment Booking
- ✅ Admin Approval for Appointment Requests
- 💳 Appointment Confirmation after Payment Verification
- 👨‍⚕️ Doctor Directory
- 🛍️ Pet Accessories Catalog
- 🛠️ Admin Dashboard for Managing Doctors, Appointments, and Products
- 📱 Responsive Web Interface

---

# ⚙️ Technologies Used

## Programming Language

- Python

## Backend

- Flask

## Frontend

- HTML5
- CSS3
- JavaScript
- Bootstrap

## Database

- MongoDB

## Libraries

- Flask
- PyMongo
- Jinja2
- Werkzeug

---

# 👥 User Roles

## 👤 User

Users can:

- Register and log in securely
- Manage pet profiles
- Book veterinary appointments
- View available doctors
- Purchase pet accessories
- Track appointment status

---

## 🛠️ Admin

Administrators can:

- Securely log in
- Manage doctor information
- Review and approve appointment requests
- Verify appointment confirmations
- Manage pet accessories
- Monitor users and appointments

---

# 📂 Project Structure

```text
centralized-pet-care-management-system/
│
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
│
├── templates/
│
├── main.py
├── MailSent.py
├── DeleteCollections.py
├── requirements.txt
├── run.bat
└── README.md
```

---

# 🔄 System Workflow

1. User registers and logs into the system.
2. User adds pet details.
3. User browses the list of available doctors.
4. User books an appointment.
5. Administrator reviews the appointment request.
6. Appointment is confirmed after approval and payment verification.
7. User can browse and purchase pet accessories through the system.

---

# 🚀 Installation & Setup

## 1. Clone the Repository

```bash
git clone https://github.com/Viiddzzz/centralized-pet-care-management-system.git
```

## 2. Navigate to the Project Folder

```bash
cd centralized-pet-care-management-system
```

## 3. Create a Virtual Environment (Optional)

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## 5. Configure MongoDB

Ensure MongoDB is installed and running locally or update the MongoDB connection string if using MongoDB Atlas.

## 6. Run the Application

```bash
python main.py
```

Open your browser and visit:

```
http://127.0.0.1:5000/
```

---

# 📸 Screenshots

Create a folder named **screenshots** inside your repository and add screenshots like these:

```text
screenshots/
├── home.png
├── login.png
├── user-dashboard.png
├── admin-dashboard.png
├── appointment.png
├── doctors.png
├── accessories.png
```

Then display them in the README:

```markdown
## Home Page

![Home](screenshots/home.png)

## Login Page

![Login](screenshots/login.png)

## User Dashboard

![User Dashboard](screenshots/user-dashboard.png)

## Admin Dashboard

![Admin Dashboard](screenshots/admin-dashboard.png)

## Appointment Booking

![Appointment](screenshots/appointment.png)

## Doctor Directory

![Doctors](screenshots/doctors.png)

## Pet Accessories

![Accessories](screenshots/accessories.png)
```

---

# 🧪 Testing

The application was tested for:

- User Registration
- Login Authentication
- Role-Based Access Control
- Appointment Booking
- Appointment Approval
- Database CRUD Operations
- Product Management
- Form Validation

---

# 🏁 Results & Insights

- Successfully implemented a centralized platform for pet care services.
- Simplified appointment scheduling through an approval workflow.
- Improved accessibility to veterinary services with a doctor directory.
- Integrated pet accessory management into a single application.
- Demonstrated secure role-based authentication and database management using Flask and MongoDB.

---

# 💼 Business Impact

- Streamlines appointment management for veterinary clinics.
- Provides pet owners with convenient access to veterinary services.
- Reduces manual administrative work through digital record management.
- Enhances customer experience with an integrated pet care platform.

---

# 🚀 Future Enhancements

- Online payment gateway integration
- Real-time appointment notifications
- Online veterinary consultation
- Mobile application (Android/iOS)
- Pet medical history management
- Product inventory management
- Cloud deployment
- Multi-clinic support

---

# ⭐ Skills Demonstrated

- Python Programming
- Flask Web Development
- MongoDB
- HTML5
- CSS3
- JavaScript
- Bootstrap
- CRUD Operations
- Authentication & Authorization
- Database Management
- Full-Stack Web Development
- Responsive Web Design

---

# 🎓 Academic Project

This project was developed as part of an academic initiative to demonstrate full-stack web application development using Flask and MongoDB with role-based authentication and centralized pet care management.

---

# 👩‍💻 Author

**Vidya S**

Aspiring Software Developer | Python & Full-Stack Web Development Enthusiast

📧 Email: vidyaa1103@gmail.com

🌐 GitHub: https://github.com/Viiddzzz

Repository: https://github.com/Viiddzzz/centralized-pet-care-management-system

---

# 📄 License

This project is licensed under the MIT License.

---

## ⭐ Support

If you found this project useful, please consider giving it a ⭐ on GitHub.

---

💡 **This project demonstrates the practical application of full-stack web development by integrating role-based authentication, veterinary appointment management, doctor information, and pet accessories into a centralized platform using Flask and MongoDB.**
