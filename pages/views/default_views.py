from django.views.generic import TemplateView
import markdown
from django.shortcuts import render
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
