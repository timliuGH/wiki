from django import forms
from django.shortcuts import render, redirect

from . import util


class SearchForm(forms.Form):
    query = forms.CharField(label="", widget=forms.TextInput(
        attrs={"class": "search", "placeholder": "Search Encyclopedia"}
    ))


class EntryForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(
        attrs={"autofocus": "autofocus"}
    ))
    entry = forms.CharField(widget=forms.Textarea(
        attrs={"rows": 20, "cols": 120}
    ))


class EditForm(forms.Form):
    title = forms.CharField(widget=forms.HiddenInput())


def index(request):
    entries = util.list_entries()

    return render(request, "encyclopedia/index.html", {
        "search_form": SearchForm(),
        "entries": entries,
    })


def search(request):
    entries = util.list_entries()

    # Get form data
    form_data = SearchForm(request.GET)

    # Process search query
    if form_data.is_valid():
        query = form_data.cleaned_data["query"]

        # Redirect to entry if entry exists
        for entry in entries:
            if query.lower() == entry.lower():
                return redirect("entry", entry)

        # List entries that have the query as a subset, case-insensitive
        # This search maintains the entry's original letter casing
        results = [entry for entry in entries if query.lower() in entry.lower()]
        return render(request, "encyclopedia/search.html", {
            "search_form": SearchForm(),
            "results": results,
        })
    else:
        # If form is invalid re-render page with existing info
        return render(request, "encyclopedia/index.html", {
            "search_form": form_data,
            "entries": entries,
        })


def entry(request, title):
    entry = util.get_entry(title)

    if not entry:
        return render(request, "encyclopedia/noentry.html")

    # Get correct casing for existing entry's title
    entries = util.list_entries()
    for existing_entry in entries:
        if title.lower() == existing_entry.lower():
            title = existing_entry

    return render(request, "encyclopedia/entry.html", {
        "search_form": SearchForm(),
        "title": title,
        "entry": entry,
        "edit": EditForm({"title": title}),
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
            existing_entry = [entry for entry in entries if title.lower() == entry.lower()]

            # If entry exists, redirect to same page with error message
            if len(existing_entry) > 0:
                return render(request, "encyclopedia/add.html", {
                    "search_form": SearchForm(),
                    "entry_form": form_data,
                    "title": existing_entry[0],
                })

            entry_text = form_data.cleaned_data["entry"]

            # Save entry to disk
            # with open('entries/'+title+'.md', 'w') as f:
                # f.write(entry_text)
            util.save_entry(title, entry_text)

            # Take user to new entry
            return redirect("entry", title)
        
        # Handle invalid form data
        else:
            return render(request, "encyclopedia/add.html", {
                "search_form": SearchForm(),
                "entry_form": form_data,
            })

    # Handle GET request (user clicks on 'Create New Page' button)
    return render(request, "encyclopedia/add.html", {
        "search_form": SearchForm(),
        "entry_form": EntryForm(),
    })


def edit(request):
    # Handle POST request (user submits edits for an entry)
    if request.method == "POST":

        # Validate form data
        form_data = EntryForm(request.POST)
        if not form_data.is_valid():
            return render(request, "encyclopedia/error.html")

        # Parse submitted form for relevant content
        title = form_data.cleaned_data["title"]
        entry = form_data.cleaned_data["entry"]

        # Save edits to disk
        util.save_entry(title, entry)

        # Redirect user to updated entry
        return redirect("entry", title)
    
    # Handle GET request (user clicked on entry's edit button)
    else:
        # Validate form data and/or request is valid
        form_data = EditForm(request.GET)
        if not form_data.is_valid():
            return render(request, "encyclopedia/error.html")
        
        # Determine which entry is being edited
        title = form_data.cleaned_data["title"]

        # Retrieve corresponding entry
        entry = util.get_entry(title)

        # Send user to new page populated with the current entry to edit
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "entry_form": EntryForm({"title": title, "entry": entry})
        })