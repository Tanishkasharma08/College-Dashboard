# College Dashboard
### ACET – Aligarh College of Engineering & Technology

A modern, fully responsive college information dashboard built with Flask and SQLite. It displays all important college information including admissions, fees, academic calendar, circulars, scholarships, and a working contact form with a secure admin panel to manage incoming messages.

---

## Features

- **College Overview** — Institution details, approval status (AICTE), and affiliation (AKTU)
- **Departments** — Dedicated cards for MBA, MCA, B.Tech, BBA, and BCA programs
- **Admission Procedure** — Program-wise eligibility criteria and required documents list
- **Fees Structure** — Year-wise fee breakup table for all 5 programs (2026–27)
- **Academic Calendar** — Color-coded calendar with exams, holidays, and vacations for 2026
- **Circulars & Notices** — Tabbed section for Notices, Events, and Scholarship updates
- **Scholarship Section** — Merit, Need-Based, Girl Student, Defence Ward, Sibling, and UP Govt. schemes
- **Contact Form** — Messages submitted via the form are saved directly to a SQLite database
- **Secure Admin Panel** — Login-protected dashboard to view, mark as read, and delete messages
- **Scroll Animations** — Smooth reveal effects using Intersection Observer API
- **Responsive Design** — Mobile-friendly layout that works on all screen sizes
- **Active Nav Highlight** — Navigation link highlights automatically based on scroll position

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, Flask |
| Database | SQLite3 |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Fonts | Google Fonts — Cormorant Garamond, Plus Jakarta Sans, JetBrains Mono |
| Auth | Flask Session-based Login |
| Templating | Jinja2 (via Flask render_template_string) |

---

## Project Structure

```
college-dashboard/
│
├── app.py              # Main Flask application (routes, DB logic, HTML templates)
├── acet_messages.db    # SQLite database — auto-created on first run
├── index.html          # Standalone static version of the frontend
└── README.md
```

---

## Installation / Setup

**Step 1 — Clone the repository**
```bash
git clone https://github.com/your-username/college-dashboard.git
cd college-dashboard
```

**Step 2 — Install dependencies**
```bash
pip install flask
```

**Step 3 — Run the application**
```bash
python app.py
```

**Step 4 — Open in your browser**

| Page | URL |
|------|-----|
| Website | http://127.0.0.1:5000/ |
| Admin Login | http://127.0.0.1:5000/admin/login |
| Admin Dashboard | http://127.0.0.1:5000/admin/messages |

**Admin Credentials**

| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | `admin123` |

