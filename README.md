# Vehicle Parking App V1

A multi-user web application to manage 4-wheeler parking lots and vehicle reservations with role-based access for administrators and users.

---

## Project Overview

This application allows administrators to create and manage parking lots and users to book available parking spots. Each lot has a custom rate, and spot allocation is automatic based on availability.

### Core Features

- **Admin (Superuser)**
  - Root access (no registration required).
  - Create, edit, or delete parking lots.
  - View status of all parking spots and parked vehicles.
  - View all registered users.
  - View detailed history of past parking reservations.

- **User**  
  - Register and login securely.
  - View available lots.
  - Reserve a spot (auto-assigned).
  - Release a spot when done.
  - View personal parking history.

### Extra Functionality

- Form validation (HTML5 + backend).
- Structured RESTful API using `Flask-RESTful`.
- Authentication & session management using `Flask-Login`.
- **Search Functionality** to quickly find relevant records.
- Responsive UI with **Bootstrap** and custom styling.

---

## Tech Stack

| Layer      | Tools/Libraries                                     |
|------------|-----------------------------------------------------|
| Frontend   | HTML, CSS, Bootstrap, JavaScript                    |
| Backend    | Flask, Flask-RESTful, Flask-SQLAlchemy, Flask-Login |
| Database   | SQLite                                              |
| Templating | Jinja2                                              |

---

## Security

- Sessions protected using `Flask-Login`.
- `SECRET_KEY` generated using `secrets.token_hex(32)`.
- Access restrictions via decorators (`@admin_required`, `@user_required`).

---

## Installation & Setup

- **Clone the repo:**
   ```bash
   git clone https://github.com/23f3001593/vehicle-parking-app-v1.git

- **Install dependencies:**
    ```bash
    pip install -r requirements.txt

- **Run the app:**
    ```bash
    python app.py

- **Visit:**
    ```bash
    http://127.0.0.1:5000

---

## Acknowledgements

> This project was independently developed by **Om Manish Makadia (23f3001593)** as part of the **MAD1 Project** for the **IITM BS Degree Program**.

---