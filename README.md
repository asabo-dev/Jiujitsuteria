# 🥋 Brazilian Jiu-Jitsu Tutorial Web App

This is a Django-based web application showcasing a curated collection of Brazilian Jiu-Jitsu (BJJ) tutorial videos, organized by techniques such as guard passes, takedowns, and submissions. The app is hosted on AWS using Free Tier resources.

## 🔧 Features

- 🎬 Categorized video tutorials (Takedowns, Guard Passes, Submissions, etc.)
- 📂 Videos stored securely on Amazon S3
- 🗂️ Admin panel to manage tutorials
- 🌍 Hosted on AWS EC2 and served via a custom domain using Route 53
- 🛢️ PostgreSQL database hosted on Amazon RDS

## 🧰 Built With

- Python 3.x
- Django 4.x
- HTML/CSS (Bootstrap or Tailwind)
- AWS Services:
  - Amazon EC2 (Hosting)
  - Amazon S3 (Video Storage)
  - Amazon RDS (Database)
  - Amazon Route 53 (Domain Routing)

## 🖼️ Screenshots

*(Insert screenshots of homepage, video sections, admin panel)*

## 🚀 Getting Started (Local Setup)

```bash
# Clone the repository
git clone https://github.com/yourusername/bjj-tutorials.git
cd bjj-tutorials

# Create virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations and start server
python manage.py migrate
python manage.py runserver
