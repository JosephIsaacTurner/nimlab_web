from django.views.generic import TemplateView
import markdown
from django.shortcuts import render
from django.http import JsonResponse
from pages.models import Dataset
from django.db import connection
import os

class HomePageView(TemplateView):
    template_name = "pages/home.html"

def usage_page_view(request, **kwargs):
    context = {}
    # We need to make the path relative to the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    markdown_path = os.path.join(project_root, "../templates/pages/usage.md")
    markdown_path = os.path.abspath(markdown_path)
    with open(markdown_path, "r") as file:
        markdown_content = file.read()
    html_content = markdown.markdown(markdown_content)
    context["html_content"] = html_content
    return render(request, "pages/usage.html", context)

def doi_suggestions(request):
    # Using raw SQL query with parameter substitution to prevent SQL injection
    raw_query = """SELECT DISTINCT doi_string 
                    FROM datasets 
                    WHERE doi_string IS NOT NULL 
                    AND doi_string <> ''"""

    with connection.cursor() as cursor:
        cursor.execute(raw_query)
        # Access the first (and only) item in each row with row[0]
        dois = [row[0] for row in cursor.fetchall()]
    
    return JsonResponse(dois, safe=False)