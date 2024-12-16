from django.urls import path
from . import views

app_name = "loansapp"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # loans management
    ## experiment with generic class based view
    path("add_loan", views.loan_add, name="loan_add"),
    path("loan_list", views.loan_list, name="loan_list"),
    path("loan_search", views.loan_search, name="loan_search"),
    path("loan_details/<int:loan_id>", views.loan_details, name="loan_details"),
    path("loan_details/<int:loan_id>/edit/", views.loan_details, {'edit': True}, name="loan_details_edit"),
    path("loan_update/<int:loan_id>", views.loan_update, name="loan_update"),

    path("add_payment/<int:loan_id>", views.loan_payment_add, name="loan_payment_add"),

    # vendors management
    path("vendors", views.vendor_list, name="vendor_list"),
    path("add_vendor", views.vendor_add, name="vendor_add"),
    path("vendor_details/<int:vendor_id>", views.vendor_details, name="vendor_details"),
    path("vendor_details/<int:vendor_id>/edit", views.vendor_details, {'edit': True}, name="vendor_details_edit"),
    path("vendor_update/<int:vendor_id>", views.vendor_update, name="vendor_update"),
]