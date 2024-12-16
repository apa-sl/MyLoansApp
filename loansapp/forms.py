from django import forms
from .models import *
import traceback

class SearchSimpleForm(forms.Form):
    search_query = forms.CharField(max_length=100,
                                    required=False,
                                    label = "Search query",
                                    widget=forms.TextInput(attrs={
                                        'placeholder': 'Search for a loan',
                                    }),
                                    )

class LoanFilterDatesForm(forms.Form):
    date_from = forms.DateField(required=False,
                                    label="From Date",
                                    widget=forms.DateInput(attrs={
                                        'type':'date',
                                    }),
    )
    date_to = forms.DateField(required=False,
                                label="To Date",
                                widget=forms.DateInput(attrs={
                                    'type':'date',
                                    }),
                                )
#TODO add logic that from has to be < than to

class NewLoanForm(forms.ModelForm):
    class Meta:
        model = Loans
        #fields = "__all__"
        exclude = ["amount_outstanding", "due_day"] # amount_outstanding have amount_total value on created copied, due_day is automaticaly calculated from the payment_start_date, status is 0 for a new loan

        widgets={
            'first_payment_date':forms.DateInput(attrs={'type':'date'}),
            'last_payment_date':forms.DateInput(attrs={'type':'date'}),
        }

    def __init__(self, *args, **kwargs):
        # catch currently logged in user info.
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            # display only vendor created by logged in user=
            self.fields['vendor'].queryset = Vendors.objects.filter(user=self.user)
        else:
            self.fields['vendor'].queryset = Vendors.objects.none()
        # make status field read-only and non-modificable for the user
        #self.fields['status'].widget.attrs['readonly'] = True # this one was not making any effect
        self.fields['status'].widget.attrs['disabled'] = 'disabled'

    #override default save for the modelForm to manipulate model fields before storing in DB
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user # save user from the request as loan user
        if not instance.pk:  # This ensures that the logic runs only when the instance is being created
            instance.status = 0
            instance.due_day = instance.first_payment_date.day
            instance.amount_outstanding = instance.amount_total
        try:
            if commit:
                instance.clean() # call model custom validators in clean() before saving instance into DB
                instance.save()
        except ValidationError as e:
            # Add model validation errors to the form
            self.add_error(None, e)
            raise e

        return instance


class EditLoanForm(forms.ModelForm):
    class Meta:
        model = Loans
        #fields = "__all__"
        exclude = ["amount_outstanding", "due_day"] # amount_outstanding have amount_total value on created copied, due_day is automaticaly calculated from the payment_start_date, status is 0 for a new loan

        widgets={
            #TODO make Status field readonly displaying Status 0 label when creating new loan
            'first_payment_date':forms.DateInput(attrs={'type':'date'}),
            'last_payment_date':forms.DateInput(attrs={'type':'date'}),
        }

    def __init__(self, *args, **kwargs):
        # get loan kwarg on form initialization
        self.loan = kwargs.pop('loan', None)

        # catch currently logged in user info.
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            # display only vendor created by logged in user
            self.fields['vendor'].queryset = Vendors.objects.filter(user=self.user)
        else:
            self.fields['vendor'].queryset = Vendors.objects.none()
        
        #make some fields non-editable for the user
        self.fields['status'].widget.attrs['disabled'] = 'disabled'
        self.fields['status'].widget = forms.HiddenInput()
        self.fields['first_payment_date'].widget.attrs['readonly'] = 'readonly'
        self.fields['last_payment_date'].widget.attrs['readonly'] = 'readonly'
        self.fields['amount_total'].widget.attrs['readonly'] = 'readonly'
        self.fields['min_installment_amount'].widget.attrs['readonly'] = 'readonly'
    
    def save(self, commit=True):
        print("EditForm save function has been launched")
        instance = super().save(commit=False)

        try:
            if commit:
                instance.clean()
                instance.save()
        except ValidationError as e:
            # Add model validation errors to the form
            self.add_error(None, e)
            raise e

        return instance


class NewPaymentForm(forms.ModelForm):
    class Meta:
        model = Payments
        exclude = ["loan",]

        widgets={
            'payment_date':forms.DateInput(attrs={'type':'date'}),
        }

    def __init__(self, *args, **kwargs):
        # get loan kwarg on form initialization
        self.loan = kwargs.pop('loan', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        """
        Override clean to set the loan before calling clean.
        """
        # Trigger a form error here for testing purposes
        if self.loan:
            self.instance.loan = self.loan
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        try:
            if commit:
                instance.clean()
                instance.save()
        except ValidationError as e:
            # Add model validation errors to the form
            self.add_error(None, e)
            raise e

        return instance


class NewVendorForm(forms.ModelForm):
    class Meta:
        model = Vendors
        fields = ["name",]

    def __init__(self, *args, **kwargs):
        # Catch the vendor argument from kwargs
        self.vendor = kwargs.pop('vendor', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data