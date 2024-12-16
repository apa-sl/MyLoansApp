
#from datetime import date

def date_add_months(source_date, months, operation="add", day="original"):
    '''
    Add (default) or optionally substract given number of months to the source date using standard datetime module
    '''
    if operation == "substract":
        months = -months
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    last_day_of_month = [31,
                        29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                        31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]
    if day == "first":
        day = 1
    elif day == "last":
        day = last_day_of_month
    elif day == "original":
        day = min(source_date.day, last_day_of_month)

    return source_date.replace(year=year, month=month, day=day)#.strftime("%Y-%m-%d")


def dates_months_diff(start_date, end_date):
    '''
    Returns int value of number of months between 2 dates
    '''
    # Extract year and month from start_date and end_date
    start_year = start_date.year
    start_month = start_date.month
    end_year = end_date.year
    end_month = end_date.month

    # Calculate the difference in years and months
    year_diff = end_year - start_year
    month_diff = end_month - start_month

    # Calculate the total difference in months
    total_months_diff = year_diff * 12 + month_diff

    return total_months_diff


def search(request, model, search_query):
    '''
    search with query through specified model
    '''
    from loansapp.models import Loans, Vendors  # Lazy import to avoid circular import issues
    from django.db.models import Q
    
    match model:
        case "loans":
            return Loans.objects.filter(Q(user=request.user) & (Q(name__icontains=search_query) | Q(vendor__name__icontains=search_query) | Q(agreement_id__icontains=search_query)))
        case "vendors":
            return Vendors.objects.filter(Q(name__icontains=search_query))
        case _:
            return Loans.objects.none()  # Default case to return an empty queryset