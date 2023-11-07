from django.shortcuts import render
from pages.forms import DatasetSearchForm
from pages.models import Dataset

from django.contrib.auth.decorators import login_required

@login_required
def search_datasets(request):
    # Initialize the form and result set
    form = DatasetSearchForm(request.GET or None)
    results = Dataset.objects.all() if request.GET and not request.GET.dict() else Dataset.objects.none()

    if request.method == 'GET' and request.GET.dict():  # Check if there are any GET parameters
        if form.is_valid():
            results = form.search()  # Get the search results if the form is valid

    return render(request, 'pages/search.html', {'form': form, 'results': results})
