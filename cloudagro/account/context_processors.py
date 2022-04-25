from land.models import Campaign

def base_data(request):
    data = {}
    
    if request.session['campaign']:
        data["campaign"] = request.session['campaign']
    elif Campaign.objects.all():
        data["campaign"] = Campaign.objects.all()[0]
    else:
        data["campaign"] = []
        
    return data