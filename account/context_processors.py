from land.models import Campaign

def base_data(request):
    data = {}

    if 'campaign' in request.session:  
        data["campaign"] = request.session['campaign']
    elif Campaign.objects.all():
        data["campaign"] = Campaign.objects.all()[0].nombre
        request.session['campaign'] = Campaign.objects.all()[0].nombre
        request.session.modified = True
    else:
        data["campaign"] = []
        request.session['campaign'] = []
    return data