import csv
from operator import itemgetter
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RecordForm
from .models import Record
from .utils import search_waste, REPORTS_COLUMNS_VALUES, REPORTS_COLUMNS_HEADER, paginate_records
from .filters import FilterRecords
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import datetime
from django.utils.dateparse import parse_date
from django.db.models import Count
from django.db.models import Sum,Avg

def records(request):
    all_records, search_query = search_waste(request)
    custom_range, all_records = paginate_records(request, all_records, 6)

    context = {'records': all_records, 'search_query': search_query, 'custom_range': custom_range}
    return render(request, 'records/records.html', context)


def record(request, pk):
    one_record = get_object_or_404(Record, id=pk)
    context = {'record': one_record}
    return render(request, 'records/single-record.html', context)


@login_required(login_url='login')
def create_record(request):
    profile = request.user.profile
    form = RecordForm()
    if request.method == 'POST':
        form = RecordForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            new_record = form.save(commit=False)
            new_record.owner = profile
            new_record.save()
            return redirect('records')

    context = {'form': form}
    return render(request, 'records/records-form.html', context)


@login_required(login_url='login')
def update_record(request, pk):
    profile = request.user.profile
    record_to_update = profile.record_set.get(id=pk)
    form = RecordForm(instance=record_to_update)
    if request.method == 'POST':
        form = RecordForm(request.POST or None, request.FILES or None, instance=record_to_update)
        if form.is_valid():
            form.save()
            return redirect('records')

    context = {'form': form}
    return render(request, 'records/records-form.html', context)


@login_required(login_url='login')
def delete_record(request, pk):
    profile = request.user.profile
    record_to_delete = profile.record_set.get(id=pk)
    form = RecordForm(instance=record_to_delete)
    if request.method == 'POST':
        record_to_delete.delete()
        return redirect('records')

    context = {'object': form}
    return render(request, 'records/delete-record.html', context)


@login_required(login_url='login')
def get_reports(request):
    summaries = Record.get_total_quantities()
    summaries_of_records = Record.get_all_records()
    all_records = Record.objects.all()
    my_filter = FilterRecords(request.GET, queryset=all_records)
    all_records = my_filter.qs

    context = {
        'summaries': summaries,
        'summaries_of_records': summaries_of_records,
        'my_filter': my_filter,
        'all_records': all_records
    }
    return render(request, 'records/reports.html', context)



@login_required(login_url='login')
def export_to_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=csv_report.csv'
    writer = csv.writer(response)

    writer.writerow(['Title: List of all waste records'])
    writer.writerow([])

    writer.writerow(REPORTS_COLUMNS_HEADER)

    # Start with all records
    records = Record.objects.all()

    # Apply filters if provided
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        panchayat = request.POST.get('panchayat')

        if start_date:
            records = records.filter(date__gte=parse_date(start_date))
        if end_date:
            records = records.filter(date__lte=parse_date(end_date))
        if panchayat:
            records = records.filter(source_panchayat__icontains=panchayat)

    # Extract values
    record_values = list(records.values_list(*REPORTS_COLUMNS_VALUES))

    # Sort while avoiding NoneType comparison issues
    sorted_records = sorted(
        record_values,
        key=lambda row: row[0] or ""  # Replace None with empty string for safe comparison
    )

    for record in sorted_records:
        writer.writerow(record)

    return response



@login_required(login_url='login')
def export_to_csv_view(request):
    return render(request, 'records/export-to-csv.html')


from datetime import datetime
from django.utils.dateparse import parse_date

@login_required(login_url='login')
def export_to_pdf(request):
    # Start with all records
    records = Record.objects.all()

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        panchayat = request.POST.get('panchayat')

        if start_date:
            records = records.filter(date__gte=parse_date(start_date))
        if end_date:
            records = records.filter(date__lte=parse_date(end_date))
        if panchayat:
            records = records.filter(source_panchayat__icontains=panchayat)

    summaries = records.aggregate(
        total_records=Count('id'),
        total_weight=Sum('weight_kg'),
        average_weight=Avg('weight_kg')
    )

    summaries_of_records = records.values(
        'date', 'vehicle_no', 'weight_kg', 'source_panchayat', 'waste_type'
    ).order_by('-date')

    summaries_county = records.values('source_panchayat').annotate(
        total_weight=Sum('weight_kg'),
        record_count=Count('id')
    ).order_by('-total_weight')

    context = {
        'all_records': records,
        'summaries': summaries,
        'summaries_of_records': summaries_of_records,
        'summaries_county': summaries_county,
    }

    # Render the template
    template_path = 'records/export-to-pdf.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="waste_evidence_report.pdf"'
    template = get_template(template_path)
    html = template.render(context)

    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response



@login_required(login_url='login')
def export_to_pdf_view(request):
    return render(request, 'records/export-to-pdf.html')
