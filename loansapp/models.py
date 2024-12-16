from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, MinLengthValidator, MaxLengthValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from decimal import Decimal
from utils import *

# Create your models here.
username_regex = RegexValidator(
    regex=r'^[0-9a-zA-Z_-]*$',
    message='Please use only supported chars'
)

class User(AbstractUser):
    # require min length 3 chars of the username
    AbstractUser._meta.get_field('username').validators = [MinLengthValidator(3), MaxLengthValidator(50)]
    AbstractUser._meta.get_field('username').validators = [username_regex]

    def __str__(self) -> str:
        return f"{self.username}"

class Statuses(models.IntegerChoices):
    UNPAID = 0, _("Unpaid")
    PAIDPARTLY = 1, _("Paid partly")
    PAID = 2, _("Paid")

class Loans(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="loans", editable=False)
    vendor = models.ForeignKey("Vendors", on_delete=models.PROTECT, related_name="loans")
    status = models.IntegerField(default=Statuses.UNPAID, choices=Statuses.choices)
    first_payment_date = models.DateField()
    last_payment_date = models.DateField()
    agreement_id = models.CharField(max_length=50)
    due_day = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(30)])
    amount_total = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    amount_outstanding = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    min_installment_amount = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    # last_edit = models.DateField(auto_now=True)

    def clean(self):
        # Custom validations for first/last_payment_date
        if self.first_payment_date and self.last_payment_date:
            if self.first_payment_date > self.last_payment_date:
                raise ValidationError({
                    'first_payment_date': 'First payment date has to be before last payment date.'
                })
            if self.first_payment_date.day != self.last_payment_date.day:
                raise ValidationError({
                    'last_payment_date': 'First & last payment dates have to be on the same day of the month.'
                })
        else:
            # Check if either date is None and raise a validation error accordingly
            if not self.first_payment_date:
                raise ValidationError({'first_payment_date': 'First payment date is required.'})
            if not self.last_payment_date:
                raise ValidationError({'last_payment_date': 'Last payment date is required.'})


class Vendors(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="vendors", editable=False)

    def __str__(self) -> str:
        return f"{self.name}"

class Installments(models.Model):
    loan = models.ForeignKey(Loans, on_delete=models.CASCADE, related_name="installments")
    amount = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_date = models.DateField(null=True)
    payment_status = models.IntegerField(default=Statuses.UNPAID, choices=Statuses.choices)

class Payments(models.Model):
    loan = models.ForeignKey(Loans, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_date = models.DateField()

    def clean(self):
        super().clean()
        
        # Validate if there is a loan provided before running other custom validations
        if not self.loan:
            raise ValidationError('Loan must be set before validating.')

        # Ensure payment_date is provided before validation
        if not self.payment_date:
            raise ValidationError({'payment_date': 'Payment date is required.'})
    
        # Custom validations for payment_date not earlier than first_payment_date in the loan model
        min_allowed_date = date_add_months(self.loan.first_payment_date, 1, "substract")
        if self.payment_date < min_allowed_date:
            raise ValidationError({
                'payment_date': f'Payment date cannot be earlier than {min_allowed_date} (1 month before the first payment date of the loan).'
            })