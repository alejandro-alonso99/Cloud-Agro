from itertools import product
from django.shortcuts import get_object_or_404, redirect, render

from .models import Land, Campaign, Lote
from .forms import LandForm, CampaignForm, LoteForm, ApplicationForm
from django.http import HttpResponseRedirect


def land_main(request):

    lands = Land.objects.all()

    return render(request,'land/land_main.html',{
                                                'lands':lands,
                                                })

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

def land_detail(request, nombre):

    land = get_object_or_404(Land, nombre=nombre)

    return render(request, 'land/land_detail.html',{
                                                'land':land,
                                                })

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

def campaign_list(request):

    campaigns = Campaign.objects.all()

    return render(request, 'land/campaign_list.html',{
                                                        'campaings':campaigns,
                                                        })

def campaign_detail(request, campaign, pk):

    campaign = get_object_or_404(Campaign, slug=campaign, pk=pk)

    return render(request, 'land/campaign_detail.html',{
                                                        'campaign':campaign,
                                                        })

def lotes_list(request):

    lotes = Lote.objects.all()


    return render(request,'land/lotes_list.html',{
                                                    'lotes':lotes
                                                })

def lote_create(request):

    if request.method == 'POST':
        lote_form = LoteForm(data=request.POST)

        if lote_form.is_valid():
            lote_form.save()

            return redirect('land:lotes_list')
        
    else:
        lote_form = LoteForm()

    return render(request, 'land/lote_create.html',{
                                                    'lote_form':lote_form,
                                                    })

def lote_detail(request,  id, lote):

    lote = get_object_or_404(Lote, id=id, slug=lote)

    product_choices = request.session.get('product_choices')

    product_choices = tuple(tuple(product) for product in product_choices)

    if request.method == 'POST':
        application_form = ApplicationForm(data=request.POST)

        if application_form.is_valid():
            application_form.save()

        
            return redirect(lote.get_absolute_url())
    else:
        application_form = ApplicationForm()

    return render(request, 'land/lote_detail.html', {
                                                        'lote':lote,
                                                        'application_form':application_form,
                                                        })