# stutern_health_guidance.views

from django.shortcuts import redirect

def index_view(request):
    return redirect('/api/docs/swagger/')