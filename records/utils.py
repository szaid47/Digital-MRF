from django.db.models import Q
from .models import Record
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

# Update report columns to include 'name'
REPORTS_COLUMNS_VALUES = ['name', 'date', 'vehicle_no', 'weight_kg', 'source_panchayat', 'waste_type']
REPORTS_COLUMNS_HEADER = ['Name', 'Date', 'Vehicle No', 'Weight (kg)', 'Source Panchayat', 'Waste Type']


def search_waste(request):
    search_query = ''
    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')

    records = Record.objects.filter(
        Q(name__icontains=search_query) |
        Q(vehicle_no__icontains=search_query) |
        Q(source_panchayat__icontains=search_query) |
        Q(waste_type__icontains=search_query)
    )

    return records, search_query


def paginate_records(request, records, results):
    page = request.GET.get('page')
    paginator = Paginator(records, results)

    try:
        records = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        records = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        records = paginator.page(page)

    left_index = (int(page) - 4)
    if left_index < 1:
        left_index = 1

    right_index = (int(page) + 5)
    if right_index > paginator.num_pages:
        right_index = paginator.num_pages + 1

    custom_range = range(left_index, right_index)

    return custom_range, records
