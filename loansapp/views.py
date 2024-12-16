from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db import IntegrityError
from datetime import datetime, date
from utils import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.views.generic.list import ListView

from django.db.models import CharField, TextField, Sum, Count, Q
from django.db.models.functions import Lower

from .models import *
from .forms import *

# Create your views here.
def index(request):
    '''
    Generates dashboard view with statistical data about logged in user loans
    '''

    def period_stats(date_start=None, date_end=None):
        '''
        calculates installments stats for a given time period (months)
        '''
        # by default set the period to the next full month
        if date_start is None and date_end is None:
            period_date_start = date_add_months(date.today(), 1, day="first")
            period_date_end = date_add_months(date.today(), 1, day="last")
        elif (date_start is None and date_end is not None) or (date_start is not None and date_end is None):
            print('Error date_start or date_end is None')
        # else set the period to selected full months
        else:
            period_date_start = date_add_months(datetime.strptime(date_start, "%Y-%m-%d"), 0, day="first")
            period_date_end = date_add_months(datetime.strptime(date_end, "%Y-%m-%d"), 0, day="last")

        # caluclate installments stats for selected period
        myloans_selectedperiod_loans_count = Loans.objects.filter(user=request.user).filter(installments__payment_date__gte=period_date_start).filter(installments__payment_date__lte=period_date_end).distinct().count()
        myloans_selectedperiod_installments_paid_amount = Installments.objects.filter(loan__user=request.user).filter(payment_date__gte=period_date_start).filter(payment_date__lte=period_date_end).filter(payment_status=2).aggregate(Sum('amount'))
        myloans_selectedperiod_installments_paid_amount = myloans_selectedperiod_installments_paid_amount[next(iter(myloans_selectedperiod_installments_paid_amount))]
        if myloans_selectedperiod_installments_paid_amount is None:
            myloans_selectedperiod_installments_paid_amount = 0
        myloans_selectedperiod_installments_unpaid_amount = Installments.objects.filter(loan__user=request.user).filter(payment_date__gte=period_date_start).filter(payment_date__lte=period_date_end).filter(payment_status=0).aggregate(Sum('amount'))
        myloans_selectedperiod_installments_unpaid_amount = myloans_selectedperiod_installments_unpaid_amount[next(iter(myloans_selectedperiod_installments_unpaid_amount))]
        if myloans_selectedperiod_installments_unpaid_amount is None:
            myloans_selectedperiod_installments_unpaid_amount = 0

        return period_date_start, period_date_end, myloans_selectedperiod_loans_count, myloans_selectedperiod_installments_paid_amount, myloans_selectedperiod_installments_unpaid_amount

    # myloans stats
    myloans_paid_amount = Loans.objects.filter(user=request.user).filter(status=2).aggregate(Sum('amount_total'))
    myloans_paid_amount = myloans_paid_amount[next(iter(myloans_paid_amount))] or 0
    myloans_paid_amount = round(myloans_paid_amount, 2)
    myloans_paid_count = Loans.objects.filter(user=request.user).filter(status=2).count()
    myloans_paid_partly_amount = Loans.objects.filter(user=request.user).filter(status=1).aggregate(Sum('amount_total'))
    myloans_paid_partly_amount = myloans_paid_partly_amount[next(iter(myloans_paid_partly_amount))] or 0
    myloans_paid_partly_count = Loans.objects.filter(user=request.user).filter(status=1).count()
    myloans_unpaid_amount = Loans.objects.filter(user=request.user).filter(status=0).aggregate(Sum('amount_total'))
    myloans_unpaid_amount = myloans_unpaid_amount[next(iter(myloans_unpaid_amount))] or 0
    myloans_unpaid_amount = round(myloans_unpaid_amount, 2)
    myloans_unpaid_count = Loans.objects.filter(user=request.user).filter(status=0).count()
    myloans_amount = myloans_paid_partly_amount + myloans_paid_amount + myloans_unpaid_amount
    myloans_count = Loans.objects.filter(user=request.user).count()

    # current month stats
    myloans_currentmonth_name = datetime.today().strftime("%B")
    myloans_currentmonth_start, myloans_currentmonth_end, myloans_currentmonth_loans_count, myloans_currentmonth_installments_paid_amount, myloans_currentmonth_installments_unpaid_amount = period_stats(date_start=date.today().strftime("%Y-%m-%d"), date_end=date.today().strftime("%Y-%m-%d"))
    myloans_currentmonth_installments_paid_amount = round(myloans_currentmonth_installments_paid_amount, 2)
    myloans_currentmonth_installments_unpaid_amount = round(myloans_currentmonth_installments_unpaid_amount, 2)
    myloans_currentmonth_start = date_add_months(date.today(), 0, day="first")
    myloans_currentmonth_end = date_add_months(date.today(), 0, day="last")


    # Get parameters from request.GET
    date_from = request.GET.get('date_from', None)
    date_to = request.GET.get('date_to', None)

    # selected period (months) stats
    myloans_selectedperiod_start, myloans_selectedperiod_end, myloans_selectedperiod_loans_count, myloans_selectedperiod_installments_paid_amount, myloans_selectedperiod_installments_unpaid_amount  = period_stats(date_from, date_to)
    myloans_selectedperiod_installments_paid_amount = round(myloans_selectedperiod_installments_paid_amount, 2)
    myloans_selectedperiod_installments_unpaid_amount = round(myloans_selectedperiod_installments_unpaid_amount, 2)

    # Initialize date filter form
    if myloans_selectedperiod_start is not None and myloans_selectedperiod_end is not None:
        initial_data = {
            'date_from': myloans_selectedperiod_start.strftime("%Y-%m-%d"),
            'date_to': myloans_selectedperiod_end.strftime("%Y-%m-%d"),
        }
        print(initial_data['date_from'], type(initial_data['date_from']))
        print(initial_data['date_to'], type(initial_data['date_to']))

    form_filter_dates = LoanFilterDatesForm(initial=initial_data)
    if form_filter_dates.is_valid():
        date_from = myloans_selectedperiod_start
        date_to = myloans_selectedperiod_end

    context = {
        "myloans_amount": myloans_amount,
        "myloans_count": myloans_count,
        "myloans_paid_amount": myloans_paid_amount,
        "myloans_paid_count": myloans_paid_count,
        "myloans_paid_partly_amount": myloans_paid_partly_amount,
        "myloans_paid_partly_count": myloans_paid_partly_count,
        "myloans_unpaid_amount": myloans_unpaid_amount,
        "myloans_unpaid_count": myloans_unpaid_count,
        "myloans_currentmonth_start" : myloans_currentmonth_start,
        "myloans_currentmonth_end" : myloans_currentmonth_end,
        "myloans_currentmonth_name" : myloans_currentmonth_name,
        "myloans_currentmonth_loans_count": myloans_currentmonth_loans_count,
        "myloans_currentmonth_installments_paid_amount": myloans_currentmonth_installments_paid_amount,
        "myloans_currentmonth_installments_unpaid_amount": myloans_currentmonth_installments_unpaid_amount,
        "form_filter_dates" : form_filter_dates,
        "myloans_selectedperiod_start" : myloans_selectedperiod_start,
        "myloans_selectedperiod_end" : myloans_selectedperiod_end,
        "myloans_selectedperiod_loans_count":myloans_selectedperiod_loans_count,
        "myloans_selectedperiod_installments_paid_amount": myloans_selectedperiod_installments_paid_amount,
        "myloans_selectedperiod_installments_unpaid_amount": myloans_selectedperiod_installments_unpaid_amount,
    }

    return render(request, "index.html", context)


## Vendors management
def vendor_list(request):
    '''
    List all vendors
    '''
    vendors = Vendors.objects.filter(user=request.user).order_by(Lower("name")).annotate(
        loans_total=Count('loans'),
        loans_inprogress=Count('loans', filter=Q(loans__status=0) | Q(loans__status=1)),
        loans_closed=Count('loans', filter=Q(loans__status=2))
    )
    paginator = Paginator(vendors, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "vendor_list.html", {
        "page_obj": page_obj
    })


def vendor_add(request):
    '''
    Add new vendor (GET: render form, POST: add to DB)
    '''
    # check if method is POST
    if request.method == "POST":
        # take in the data submitted by the user and save it as a form
        form = NewVendorForm(request.POST)
        # check if form data is valid (server-side)
        if form.is_valid():
            # save vendor to DB
            # create new vendor object, but don't save to db yet
            new_vendor = form.save(commit=False)
            # set user field for the currently logged in user
            new_vendor.user = request.user
            # save update new_vendor to db
            new_vendor.save()
            # redirect user back to the vendors list view
            # TODO message that added successfuly
            # messages.add_message(request, messages.SUCCESS, "new vendor has been added") # propoer way of adding a message without a shortcut
            messages.success(request, "New Vendor has been added.")
            return HttpResponseRedirect(reverse("loansapp:vendor_list"))
        else:
            # store form errors in session so form rendered in other view functions will also get them
            request.session['vendor_form_data'] = request.POST
            request.session['vendor_form_errors'] = form.errors
            messages.error(request, "There were errors in the add vendor form.")
            return HttpResponseRedirect(reverse("loansapp:vendor_add"))

    # Retrieve loan edit form data and errors from session
    vendor_add_form_data = request.session.pop('vendor_form_data', None)
    vendor_add_form_errors = request.session.pop('vendor_form_errors', None)
    if vendor_add_form_data:
        form_vendor_add = NewVendorForm(vendor_add_form_data)
        if vendor_add_form_errors:
            form_vendor_add.errors.update(vendor_add_form_errors)
    else:
        form_vendor_add = NewVendorForm() 
    return render(request, "vendor_add.html", {
        "form_vendor_add": form_vendor_add 
    })


def vendor_details(request, vendor_id, edit=False):
    '''
    Display given vendor instance details & edit form
    '''
    vendor = Vendors.objects.get(pk=vendor_id)
    
    # Retrieve vendor edit form data and errors from session
    vendor_edit_form_data = request.session.pop('vendor_edit_form_data', None)
    vendor_edit_form_errors = request.session.pop('vendor_edit_form_errors', None)
    if vendor_edit_form_data:
        form_vendor_edit = NewVendorForm(vendor_edit_form_data, vendor=vendor)
        if vendor_edit_form_errors:
            form_vendor_edit.errors.update(vendor_edit_form_errors)
    else:
        form_vendor_edit = NewVendorForm(instance=vendor)

    vendor.edit = edit
    return render(request, "vendor_details.html", {
        "vendor" : vendor,
        "form_vendor_edit": form_vendor_edit,
    })


def vendor_update(request, vendor_id):
    '''
    Update details of a given vendor instance
    '''
    if request.method == "POST":
        vendor_instance=Vendors.objects.get(pk=vendor_id)
        # take in the data submitted by the user and save it as a form
        form = NewVendorForm(request.POST, instance=vendor_instance)

        # check if form data is valid (server-side)
        if form.is_valid():
                # save loan update to DB
                form.save() # save into database
                # redirect user back to the vendors list view
                messages.success(request, f"Vendor {vendor_instance.name} has been updated.")
                return HttpResponseRedirect(reverse("loansapp:vendor_details", kwargs={"vendor_id":vendor_id}))


## Loans management
def loan_list(request):
    '''
    list all loans with optional filters
    params:
    sort_order: asc, desc
    filter_by: all, unpaid, paid
    date_from/to: loans that have installments payment dates in between OR None = no dates constrain.
    '''
    # Get parameters from request.GET
    sort_by = request.GET.get('sort_by', 'last_payment_date')
    sort_order = request.GET.get('sort_order', 'asc')
    filter_by = request.GET.get('filter_by', 'all')
    date_from = request.GET.get('date_from', None)
    date_to = request.GET.get('date_to', None)

    # if there is no loans query_set passed, create one with all loans    
    if not request.session.get('search_query', ''):
        loans = Loans.objects.filter(user=request.user)
    else:
        loans = search(request, "loans", request.session['search_query'])

    # Initialize search form
    if request.session.get('search_query'):
        initial_data = {'search_query' : request.session['search_query'],
        }
        form_search = SearchSimpleForm(initial=initial_data)
    else:
        form_search = SearchSimpleForm

    # Initialize date filter form
    form_filter_dates = LoanFilterDatesForm(request.GET or None)
    if form_filter_dates.is_valid():
        date_from = form_filter_dates.cleaned_data.get('date_from')
        date_to = form_filter_dates.cleaned_data.get('date_to')
        

    # Fitering - apply status filter
    request.session['filter_by'] = filter_by
    match filter_by:
        case 'unpaid':
            loans = loans.filter(status__in=[0,1])
        case 'paid':
            loans = loans.filter(status=2)
        case 'all':
            pass

    # Filtering - apply dates filter
    if date_from and date_to:
        loans = loans.filter(
            installments__payment_date__gte=date_from,
            installments__payment_date__lte=date_to
        ).distinct()
    elif date_from:
        loans = loans.filter(
            installments__payment_date__gte=date_from
        ).distinct()
    elif date_to:
        loans = loans.filter(
            installments__payment_date__lte=date_to
        ).distinct()

    # Apply sorting
    # exculde params for template url checkout that the links will include all passed in get params (due to {% if %} limitaion in the django template)
    url_sort_exclude_params = ['sort_by', 'sort_order']
    # check if sorting field is a string or not
    field = Loans._meta.get_field(sort_by)
    # if yes, sort case insensitive
    if isinstance(field, (CharField, TextField)):
        # Annotate the queryset with the lowercased version of the field for sorting
        loans = loans.annotate(lower_sort_by=Lower(sort_by))
        if sort_order == 'asc':
            loans = loans.order_by('lower_sort_by')
        elif sort_order == 'desc':
            loans = loans.order_by('-lower_sort_by')
    else:
        if sort_order == 'asc':
            loans = loans.order_by(sort_by)
        elif sort_order == 'desc':
            loans = loans.order_by('-' + sort_by)

    # Pagination
    paginator = Paginator(loans, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)



    # render template with all passed data
    return render(request, "loan_list.html", {
        "page_obj" : page_obj,
        'exclude_params': url_sort_exclude_params,
        "form_search" : form_search,
        "form_filter_dates" : form_filter_dates,
    })


def loan_search(request, search_query=None):
    '''
    returns queryset into the session with loans containing given keyword
    '''
    if request.method == 'POST':
        request.session['search_query'] = request.POST['search_query']
        #search_query = request.session['search_query']
        #loans_search_results = search(request, "loans", search_query)
        print(request.session['search_query'])
        #return loan_list(request, loans_search_results)
        return HttpResponseRedirect(reverse('loansapp:loan_list'))


def loan_add(request):
    '''
    Add new loan
    '''
    def loan_repayment_schedule_create(loan):
        '''
        Generates loan repayment schedule for a given loan
        '''
        no_of_full_installments = dates_months_diff(loan.first_payment_date, loan.last_payment_date) + 1
        
        if (loan.amount_total % loan.min_installment_amount != 0) or (loan.amount_total - (no_of_full_installments * loan.min_installment_amount) > 0):
            no_of_full_installments -= 1 # we need to remove last full installment and replace it with reduced installment.
            last_reduced_installment_amount = loan.amount_total - (no_of_full_installments * loan.min_installment_amount)
        installment_payment_date = loan.first_payment_date
        for installment in range(no_of_full_installments):
            Installments.objects.create(loan=loan, amount = loan.min_installment_amount, payment_date = installment_payment_date)
            installment_payment_date = date_add_months(installment_payment_date, 1)
        # to keep reduced last installment as last when sorting with installment ID, adding to DB after adding full installments
        if (loan.amount_total % loan.min_installment_amount != 0) or (loan.amount_total - (no_of_full_installments * loan.min_installment_amount) > 0):
            Installments.objects.create(loan=loan, amount = last_reduced_installment_amount, payment_date = installment_payment_date)
        return
    
    # check if method is POST
    if request.method == "POST":
        # take in the data submitted by the user and save it as a form
        form = NewLoanForm(request.POST, user=request.user)
        # check if form data is valid (server-side)
        if form.is_valid():
                # save loan to DB
                form.save() # save into database
                print("Form submitted")
                loan_repayment_schedule_create(form.instance) # create&save repayment schedule to DB
                # redirect user back to the vendors list view
                messages.success(request, f"New loan {form.cleaned_data['name']} has been saved.")
                return HttpResponseRedirect(reverse("loansapp:loan_list"))
        else:
            print(request.POST.get('first_payment_date'))

            # show error msg, #TODO to check if form data will be restored or empty form dei
            messages.error(request, "There are errors in new loan form.")
            return render(request, "loan_add.html", {
                "form_loan_new": form
            })
        
    return render(request, "loan_add.html", {
        "form_loan_new": NewLoanForm(user=request.user)
    })


def loan_details(request, loan_id, edit=False):
    '''
    displays all details of a given loan
    '''
    loan = Loans.objects.get(pk=loan_id)

    # Retrieve payment form data and errors from session
    payment_form_data = request.session.pop('payment_form_data', None)
    payment_form_errors = request.session.pop('payment_form_errors', None)
    if payment_form_data:
        form_payment_add = NewPaymentForm(payment_form_data, loan=loan)
        if payment_form_errors:
            form_payment_add.errors.update(payment_form_errors)
    else:
        form_payment_add = NewPaymentForm(loan=loan)

    # Retrieve loan edit form data and errors from session
    loan_edit_form_data = request.session.pop('loan_edit_form_data', None)
    loan_edit_form_errors = request.session.pop('loan_edit_form_errors', None)
    if loan_edit_form_data:
        form_loan_edit = EditLoanForm(loan_edit_form_data, instance=loan, user=request.user)
        if loan_edit_form_errors:
            form_loan_edit.errors.update(loan_edit_form_errors)
    else:
        form_loan_edit = EditLoanForm(instance=loan, user=request.user)

    installments = loan.installments.all().order_by('payment_date')
    payments = loan.payments.all().order_by('payment_date')
    loan.edit = edit

    return render(request, "loan_details.html", {
        "loan" : loan,
        "installments" : installments,
        "payments" : payments,
        "form_payment_add" : form_payment_add,
        "form_loan_edit": form_loan_edit,
    })


def loan_update(request, loan_id):
    '''
    update given loan data based on passed loan edit form
    '''
    # parse form data, update model instance, render loan details with updated data
    if request.method == "POST":
        loan_instance=Loans.objects.get(pk=loan_id)
        # take in the data submitted by the user and save it as a form
        form = EditLoanForm(request.POST, instance=loan_instance, user=request.user)

        # check if form data is valid (server-side)
        if form.is_valid():
                # save loan update to DB
                form.save() # save into database
                #loan_repayment_schedule_update(loan) # update repayment schedule in the DB
                # redirect user back to the loans list view
                messages.success(request, f"Loan {form.cleaned_data['name']} has been updated.")
                return HttpResponseRedirect(reverse("loansapp:loan_details", kwargs={"loan_id":loan_id}))
        else:
            # store form errors in session so form rendered in other view functions will also get them
            request.session['loan_edit_form_data'] = request.POST
            request.session['loan_edit_form_form_errors'] = form.errors
            messages.error(request, "There are errors in the loan edit form.")
            return HttpResponseRedirect(reverse("loansapp:loan_details_edit", kwargs={"loan_id":loan_id}))
    

def loan_repayment_schedule_update(loan):
    '''
    recalculate installment schedule for a given loan
    '''
    # calculate total amount paid for the loan & update loan.amount_outstanding
    payments = Payments.objects.filter(loan=loan)
    amount_paid = sum(payment.amount for payment in payments)
    loan.amount_outstanding = loan.amount_total - amount_paid
    # update loan status
    if loan.amount_outstanding > 0 and loan.amount_total > amount_paid:
        loan.status = 1
    elif loan.amount_total <= amount_paid:
        loan.status = 2
    loan.save()

    # check installments schedule, update their statuses if needed (unpaid->paidpartly->paid)
    installments = Installments.objects.filter(loan=loan).order_by('payment_date')
    installments_total = 0
    for installment in installments:
        # calculate the amount already paid so far including this installment
        installments_total += installment.amount
        # skip already paid installment
        if installment.payment_status == 2:
            continue

        # mark installment PAID if the amount_paid covers this installment fully
        if installments_total <= amount_paid:
            installment.payment_status = 2
            installment.save()

        else:
            # If the total paid does not fully cover this installment, mark it as PAIDPARTLY
            if amount_paid > (installments_total - installment.amount):
                installment.payment_status = 1
                installment.save()
            break


def loan_payment_add(request, loan_id):
    '''
    adds payment to a given loan and recalculates installment schedule status
    '''
    if request.method == "POST":
        loan=Loans.objects.get(pk=loan_id)
        # take in the data submitted by the user and save it as a form
        form = NewPaymentForm(request.POST, loan=loan)

        # check if form data is valid (server-side)
        if form.is_valid():
                # save payment to DB
                form.save() # save into database
                loan_repayment_schedule_update(loan) # update repayment schedule in the DB
                # redirect user back to the vendors list view
                messages.success(request, f"Payment of {form.cleaned_data['amount']} has been added to loan {loan.name}.")
                return HttpResponseRedirect(reverse("loansapp:loan_details", kwargs={"loan_id":loan_id}))
        else:
            # store form errors in session so form rendered in other view functions will also get them
            request.session['payment_form_data'] = request.POST
            request.session['payment_form_errors'] = form.errors
            messages.error(request, "There were errors in the add payment form.")
            return HttpResponseRedirect(reverse("loansapp:loan_details", kwargs={"loan_id":loan_id}))


def login_view(request):
    '''
    displays log in form & checks if user has logged in
    '''
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            messages.success(request, "You have been logged in.")
            return HttpResponseRedirect(reverse("loansapp:index"))
        else:
            messages.error(request, "Invalid username and/or password.")
            return render(request, "login.html")
    else:
        return render(request, "login.html")


def logout_view(request):
    '''
    logs out the user and redirects to index
    '''
    logout(request)
    messages.success(request, "You have been logged out.")
    return HttpResponseRedirect(reverse("loansapp:index"))


def register(request):
    '''
    new user registration
    '''
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.error(request, "Passwords must match")
            return render(request, "register.html")

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            messages.error(request, "Username already taken") # not the best security practice, #TODO to be improved (generic message + email link?)
            return render(request, "register.html")
        login(request, user)
        messages.success(request, "You have been registered & logged in.")
        return HttpResponseRedirect(reverse("loansapp:index"))
    else:
        return render(request, "register.html")