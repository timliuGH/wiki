from django import forms
from django.shortcuts import render, redirect

from . import util

class SearchForm(forms.Form):
    search_query = forms.CharField(label="", widget=forms.TextInput(
        attrs={ "class": "search", "placeholder": "Search Encyclopedia"}
    ))

def index(request):
    entries = util.list_entries()

    # Handle POST request
    if request.method == "POST":

        # Get form data
        form = SearchForm(request.POST)

        # Process search query
        if form.is_valid():
            search_query = form.cleaned_data["search_query"]

            # Redirect to entry if entry exists
            if search_query in [entry.lower() for entry in entries]:
                return redirect("entry", search_query)

            # List entries that have the query as a subset, case-insensitive
            else:
                results = [entry for entry in entries if search_query in entry or search_query in entry.lower()]
                return render(request, "encyclopedia/search.html", {
                    "form": form,
                    "results": results,
                })

        else:
            # If form is invalid re-render page with existing info
            return render(request, "encyclopedia/index.html", {
                "form": form,
                "entries": entries,
            })

    # Handle GET request
    return render(request, "encyclopedia/index.html", {
        "form": SearchForm(),
        "entries": entries,
    })


def entry(request, title):
    entry = util.get_entry(title)

    if not entry:
        title = "Error: No Entry Found"
        entry = "This wiki does not have an article with this exact name."

    return render(request, "encyclopedia/entry.html", {
        "form": SearchForm(),
        "title": title,
        "entry": entry,
    })
