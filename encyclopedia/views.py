from django.shortcuts import render

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    entry = util.get_entry(title)

    if not entry:
        title = "Error: No Entry Found"
        entry = "This wiki does not have an article with this exact name."

    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "entry": entry,
    })
