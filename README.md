# MY LOANS APP V2
A final project for CS50W course from HarvardX. First full-stack app with full-blown functionality without cutting corners wrote from A to Z by me personally.

Video demo: https://youtu.be/XHqaUrdwQ-g

## App purpose
Track all personal loans repayments including:
- how much installemts there are to be paid this/next month or in selected time period (months,)
- summary of all loans (total, in progress, not paid, fully paid)

## Functionalities:
- dashboard with all loans summary, this months, selected period loans summary and option to view detailed list of loans for each section of the dashboard.
- full list of all loans with sorting (all columns), filtering (payment statues, dates) and search (loan name).
- details of selected loan with all it's descriptive details, installment plan & actual payments, option to add payment.
- loan vendors listing & simple management.

## Tech stack
- Database: SQlite
- Backend: Python + Django
- Frontend: Django Templates + Tailwind CSS

# Distinctiveness and Complexity
- It is my own project fullfilling personal need (to replace Excel based loans management).
- It utilizes Django with 15 view functions, 6 models, 6 class forms, 9 template views.
- UX is using Tailwind CSS and was optimized for proper responsive rendering on smaller devices.

# Files structure
- All standard elements (including views.py, urls.py, models.py)
- Templates folder - all Django templates used in the project with includes subfolder that holds all templates shared in multiple places (quasi components)
- utils.py with a few functions reused in multiple view functions.
- forms.py hold all class based forms. Due to Tailwind CSS usage custom forms that uses data & logic of class forms have been created in the template files.
- tailwind related files

# How to run the application
1. Enter main folder of the project.
2. Create a fresh SQLite database file by running:
2.1. python manage.py makemigrations (will create migration files based on the models.py)
2.2. python manage.py migrate (will apply migrations to the database)
3. Just in case run ./tailwindcss -i ./loansapp/static/css/input.css -o ./loansapp/static/css/output.css --watch to rebuild output.css file.
4. run "python manage.py runserver"
5. Access the app in your browser under http://127.0.0.1:8000/