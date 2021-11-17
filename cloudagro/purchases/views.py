from django.shortcuts import get_object_or_404, redirect, render
from .models import Animal, Purchases
from .forms import AnimalFormset, SearchForm, PurchaseForm
from django.contrib.postgres.search import SearchVector
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.db import models, transaction
from payments.forms import PaymentForm
from payments.models import Payments

@login_required
def purchase_list(request):
    purchases = Purchases.objects.all()
    total_purchases = purchases.count()

    unpayed_purchases = Purchases.objects.filter(status='por pagar')
    total_unpayed_purchases = unpayed_purchases.count()


    amount_to_pay_total=[]
    for purchase in unpayed_purchases:
        amount_to_pay = purchase.calculate_amount_to_pay()
        amount_to_pay_total.append(amount_to_pay)

    amount_to_pay_total = sum(amount_to_pay_total)

    return render(request, 'purchases/purchase_list.html', 
                                    {'purchases' : purchases,
                                    'amount_to_pay_total':amount_to_pay_total,
                                    'total_unpayed_purchases':total_unpayed_purchases,
                                    'total_purchases':total_purchases,
                                    })

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
    
    kg_neto =  purchase.brute_kg - (purchase.brute_kg * (purchase.desbaste/100)) 

    try:   
        kg_cabeza = kg_neto / purchase.total_animals
    except ZeroDivisionError:
        kg_cabeza = 0

    animals = purchase.animal_set.all()

    kg_totales=[]
    for animal in animals:
        kg_totales.append(animal.cantidad * kg_cabeza)

    animal_cabezas = list(map(int,animals.values_list('cantidad', flat=True)))

    animal_precio_kg =list(map(int,animals.values_list('precio_por_kg', flat=True)))

    sub_totals= [a * b for a, b in zip(animal_precio_kg, kg_totales)]

    animal_ivas = list(map(int,animals.values_list('iva', flat=True)))

    animal_totals = [a + b for a, b in zip(animal_ivas, sub_totals)]

    total_sub_totals = sum(sub_totals)

    total_cabezas = sum(animal_cabezas)

    total_ivas = sum(animal_ivas)

    purchase_total = sum(animal_totals)

    total_kg_total = sum(kg_totales)

    # PAGOS #
    payments = purchase.payments

    total_payed = sum(list(map(int,payments.values_list('monto', flat=True))))

    if purchase_total - total_payed <=0:
        purchase.change_status('pagado')
        purchase.save()


    initial_payment_data = {
        'content_type': purchase.get_content_type,
        'object_id': purchase.id,
    }

    payment_form = PaymentForm(request.POST or None, initial= initial_payment_data)

    if payment_form.is_valid():
        content_type = payment_form.cleaned_data.get('content_type')
        obj_id = payment_form.cleaned_data.get('object_id')
        monto = payment_form.cleaned_data.get('monto')
        tipo = payment_form.cleaned_data.get('tipo')

        attrs = {'content_type':content_type, 'object_id':obj_id, 'monto':monto, 'tipo':tipo}

        new_payment = Payments(**attrs)
        new_payment.save()

        return redirect(purchase.get_absolute_url())


    return render(request, 'purchases/purchase_detail.html',
                                    {'purchase' : purchase,
                                    'animals': animals,
                                    'kg_neto': kg_neto,
                                    'kg_cabeza':kg_cabeza,
                                    'kg_totales' : kg_totales,
                                    'animal_cantidades':animal_precio_kg,
                                    'sub_totals':sub_totals,
                                    'animal_ivas':animal_ivas,
                                    'animal_totals':animal_totals,
                                    'total_cabezas':total_cabezas,
                                    'total_sub_totals':total_sub_totals,
                                    'total_ivas':total_ivas,
                                    'purchase_total':purchase_total,
                                    'total_kg_total':total_kg_total,
                                    'payment_form':payment_form,
                                    'payments':payments,
                                    })



class PurchaseCreate(CreateView):
    model = Purchases
    fields = ['client', 'total_animals', 'brute_kg', 'desbaste']


class PurchaseAnimalsCreate(CreateView):
    model = Purchases
    fields = ['client', 'total_animals', 'brute_kg', 'desbaste']

    def get_context_data(self, **kwargs):
        data = super(PurchaseAnimalsCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['animals'] = AnimalFormset(self.request.POST)
        else:
            data['animals'] = AnimalFormset()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        animals = context['animals']
        with transaction.atomic():
            self.object = form.save()
        
            if animals.is_valid():
                animals.instance = self.object
                animals.save()
        return super(PurchaseAnimalsCreate, self).form_valid(form)    
                                                    
