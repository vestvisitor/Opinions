from django.shortcuts import render
from django.template import loader

def index(request):
    if request.user.is_authenticated:
        return render(
            request,
            "website/index_page.html",
            context={"authenticated": True}
        )
    else:
        return render(
            request,
            "website/index_page.html"
        )
