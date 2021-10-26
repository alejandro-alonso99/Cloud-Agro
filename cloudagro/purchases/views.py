from django.db.models.query import InstanceCheckMeta, QuerySet
from django.forms.models import inlineformset_factory
from django.http import request
from django.shortcuts import get_object_or_404, render
from .models import Animal, Purchases
from .forms import SearchForm, PurchaseForm
from django.contrib.postgres.search import SearchVector
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView


@login_required
def purchase_list(request):
    purchases = Purchases.objects.all()
    return render(request, 'purchases/purchase_list.html', 
                                    {'purchases' : purchases})

@login_required
def purchase_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Purchases.objects.annotate(search=SearchVector('client','date'),).filter(search=query)
    return render(request, 'purchases/search.html', {'form':form,
                                                            'query':query,
                                                            'results':results})


@login_required
def purchase_detail(request, year, month, day, purchase):
    purchase = get_object_or_404(Purchases, slug=purchase,
                                                date__year = year,
                                                date__month = month,
                                                date__day = day )
    
    return render(request, 'purchases/purchase_detail.html',
                                    {'purchase' : purchase})



@login_required
def create_purchase(request):
    new_purchase = None
    AnimalFormset = inlineformset_factory(Purchases, Animal, fields=('name','quantity','price_kg','iva'),
                                            extra=1, can_delete=True)
    purchase_form = PurchaseForm(request.POST or None, request.FILES or None)
    formset = AnimalFormset(request.POST or None, request.FILES or None)

    if purchase_form.is_valid() and formset.is_valid():

        new_purchase = purchase_form.save()

        for form in formset.forms:
            animal = form.save(commit=False)
            animal.purchase = new_purchase
            animal.save()

    return render(request, 'purchases/create_purchase.html', {'new_purchase':new_purchase,
                                                'purchase_form':purchase_form,
                                                'formset':formset,})
                                                    
