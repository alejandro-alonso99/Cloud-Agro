from itertools import product
from django.shortcuts import get_object_or_404, redirect, render
from .models import Land, Campaign
from .forms import CampaignForm, LandForm
from django.contrib.auth.decorators import login_required

@login_required
def land_main(request):

    lands = Land.objects.all()

    return render(request,'land/land_main.html',{
                                                'lands':lands,
                                                })

@login_required
def land_create(request):

    if request.method == 'POST':
        land_form = LandForm(data=request.POST)

        if land_form.is_valid():
            land_form.save()
        
        
        return redirect('land:land_main')
        
    else:
        land_form = LandForm()

    return render(request, 'land/land_create.html',{
                                            'land_form':land_form,
                                            })

@login_required
def land_detail(request, nombre):

    land = get_object_or_404(Land, nombre=nombre)

    return render(request, 'land/land_detail.html',{
                                                'land':land,
                                                })

@login_required
def campaign_create(request):

    campaigns = Campaign.objects.all()

    if request.method == 'POST':
        campaign_form = CampaignForm(data=request.POST)

        if campaign_form.is_valid():
            campaign_form.save()

            for campaign in campaigns:
                campaign.estado = 'cerrada'
                campaign.save()      

            last_camp = list(campaigns)[0]      

            last_camp.estado = 'vigente'
            last_camp.save()
        
        return redirect('land:campaign_list')
        
    else:
        campaign_form = CampaignForm()

    return render(request, 'land/campaign_create.html',{
                                            'campaign_form':campaign_form,
                                            })
                                            
@login_required
def campaign_list(request):

    campaigns = Campaign.objects.all()

    return render(request, 'land/campaign_list.html',{
                                                        'campaings':campaigns,
                                                        })
@login_required
def campaign_detail(request, campaign, pk):

    campaign = get_object_or_404(Campaign, slug=campaign, pk=pk)

    return render(request, 'land/campaign_detail.html',{
                                                        'campaign':campaign,
                                                        })

