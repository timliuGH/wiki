from django import forms
from django.shortcuts import render, redirect

from . import util


class SearchForm(forms.Form):
    search_query = forms.CharField(label="", widget=forms.TextInput(
        attrs={ "class": "search", "placeholder": "Search Encyclopedia"}
    ))


class EntryForm(forms.Form):
    title = forms.CharField()
    entry = forms.CharField(widget=forms.Textarea(
        attrs={"rows": 20, "cols": 120}
    ))


def index(request):
    entries = util.list_entries()

    # Handle POST request
    if request.method == "POST":

        # Get form data
        form_data = SearchForm(request.POST)

        # Process search query
        if form_data.is_valid():
            search_query = form_data.cleaned_data["search_query"]

            # Redirect to entry if entry exists
            if search_query in [entry.lower() for entry in entries]:
                return redirect("entry", search_query)

            # List entries that have the query as a subset, case-insensitive
            else:
                # This search maintains the entry's original letter casing
                results = [entry for entry in entries if search_query in entry or search_query in entry.lower()]
                return render(request, "encyclopedia/search.html", {
                    "search_form": form_data,
                    "results": results,
                })

        else:
            # If form is invalid re-render page with existing info
            return render(request, "encyclopedia/index.html", {
                "search_form": form_data,
                "entries": entries,
            })

    # Handle GET request
    return render(request, "encyclopedia/index.html", {
        "search_form": SearchForm(),
        "entries": entries,
    })


def entry(request, title):
    entry = util.get_entry(title)

    if not entry:
        title = "Error: No Entry Found"
        entry = "This wiki does not have an article with this exact name."

    return render(request, "encyclopedia/entry.html", {
        "search_form": SearchForm(),
        "title": title,
        "entry": entry,
    })


def add(request):
    entries = util.list_entries()

    # Handle POST request
    if request.method == "POST":

        # Get form data
        form_data = EntryForm(request.POST)

        # Process form data
        if form_data.is_valid():
            title = form_data.cleaned_data["title"]

            # Find entry with same name and retrieve correct letter casing
            existing_entry = [entry for entry in entries if title in entry or title in entry.lower()]

            # If entry exists, redirect to same page with error message
            if len(existing_entry) > 0:
                return render(request, "encyclopedia/add.html", {
                    "search_form": SearchForm(),
                    "entry_form": form_data,
                    "title": existing_entry[0],
                })

            entry_text = form_data.cleaned_data["entry"]

            # Save entry to disk
            with open('entries/'+title+'.md', 'w') as f:
                f.write(entry_text)

            # Take user to new entry
            return redirect("entry", title)
        
        # Handle invalid form data
        else:
            return render(request, "encyclopedia/add.html", {
                "search_form": SearchForm(),
                "entry_form": form_data,
            })

    # Handle GET request
    return render(request, "encyclopedia/add.html", {
        "search_form": SearchForm(),
        "entry_form": EntryForm(),
    })
