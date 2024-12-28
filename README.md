# MY LOANS APP V2

A final project for CS50W course from HarvardX. First full-stack app with full-blown functionality without cutting corners wrote from A to Z by me personally.

Video demo: https://youtu.be/XHqaUrdwQ-g

## App purpose

Track all personal loans repayments including:

- how much installemts there are to be paid this/next month or in selected time period (months,)
- summary of all loans (total, in progress, not paid, fully paid)

## Functionalities

- dashboard with all loans summary, this months, selected period loans summary and option to view detailed list of loans for each section of the dashboard.
- full list of all loans with sorting (all columns), filtering (payment statues, dates) and search (loan name).
- details of selected loan with all it's descriptive details, installment plan & actual payments, option to add payment.
- loan vendors listing & simple management.

## Tech stack

- Database: SQlite
- Backend: Python + Django
- Frontend: Django Templates + Tailwind CSS + Alpine.js

# Distinctiveness and Complexity

- It is my own project fullfilling a personal need (to replace Excel based loans management).
- It utilizes Django with 15 view functions, 6 models, 6 class forms, 9 template views, 4 custom forms.
- UI is Javascript based framework Alpine.js for client-side interactivity (mobile/desktop menu, currently selected menu option, system messages popups) and is using Tailwind CSS for styling.
- UI is handling responsive rendering for mobile & smaller devices.

# Files structure

- loansapp: folder with the app

  - templates: django templates files.
    - includes: subfolder with reusable template components
      - filter_dates.html - html code for component that filters loans by first & last instalment required payment dates
      - header_page.html - html code for each webpage header styling
      - messages.html - html & js code for messages popups rendering
      - paginator.html - html code for lists paginator rendering
      - search_simple - html code for simple loans search component.
    - index.html - template for dashboard view after login in
    - layout.html - template for navigation component
    - loan_add.html - template for new load custom form
    - loan_details.html - template for displaying specific loan's details
    - loan_list.html - template for displaying list of loans for a given user.
    - login.html - template for login view
    - register.html - template for create new account.
    - vendor_add.html - template for new vendor custom form.
    - vendor_details.html - template for displaying specific vendor custom edit form.
    - vendor_list.html - template for displaying given user's vendors list.
  - apps.py - project's app configuration (1 app).
  - forms.py - all (6) class forms definitions for the app.
  - middleware.py - configuration of LoginRequiredMiddleWare to exclude selected view from user being logged in requirement.
  - models.py - all (6) models used in the app.
  - urls.py - definitions of available urls for the app (e.g. for loans & vendors)
  - views.py - all (15) view functions used in the app for login/registration, data calculations, displaying dashboard, loans management, vendors management.

- README.md - (this file) app description & how to launch it
- tailwind.config.js - Tailwind CSS configuration file (e.g. location of html files, forms plugin)
- utils.py - 3 functions reaused within the views functions.

- All standard elements (including views.py, urls.py, models.py)
- Templates folder - all Django templates used in the project with includes subfolder that holds all templates shared in multiple places (quasi components)
- utils.py with a few functions reused in multiple view functions.
- forms.py hold all class based forms. Due to Tailwind CSS usage custom forms that uses data & logic of class forms have been created in the template files.
- tailwind related files

# How to run the application

1. Clone this repository.
2. Install dependencies.
3. Enter main folder of the project.
4. Create a fresh SQLite database file by running:
   2.1. python manage.py makemigrations (will create migration files based on the models.py)
   2.2. python manage.py migrate (will apply migrations to the database)
5. Just in case run ./tailwindcss -i ./loansapp/static/css/input.css -o ./loansapp/static/css/output.css --watch to rebuild output.css file.
6. run "python manage.py runserver"
7. Access the app in your browser under http://127.0.0.1:8000/
