from django.conf import settings

from land.models import Campaign

def base_data(request):
    data = {}

    if Campaign.objects.all():
        data["campaign"] = Campaign.objects.all()[0]
    
    elif request.session['campaign']:
        data["campaign"] = request.session['campaign']
    else:
        data["campaign"] = []
        
    return data