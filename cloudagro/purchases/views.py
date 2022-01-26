from django.shortcuts import get_object_or_404, redirect, render

from .models import Animal, Purchases
from .forms import AnimalForm, SearchForm, PurchaseForm
from django.contrib.postgres.search import SearchVector
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.db import models, transaction
from payments.forms import PaymentForm, SelfChecksForm, EndorsedChecksForm
from payments.models import Payments, SelfChecks, EndorsedChecks, ThirdPartyChecks
from django.forms.models import modelformset_factory

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

    self_checks = purchase.self_checks

    endorsed_checks = purchase.endorsed_checks

    third_p_checks = ThirdPartyChecks.objects.filter(estado='a depositar')

    if purchase.calculate_amount_to_pay() <= 0:
        purchase.change_status('pagado')
        purchase.save()
        
    initial_payment_data = {
        'content_type': purchase.get_content_type,
        'object_id': purchase.id,
    }

    payment_form = PaymentForm(request.POST or None, initial= initial_payment_data)

    self_check_form =SelfChecksForm(request.POST or None, initial=initial_payment_data)

    endorsed_checks_form = EndorsedChecksForm(request.POST or None, initial=initial_payment_data)

    if payment_form.is_valid():
        content_type = payment_form.cleaned_data.get('content_type')
        obj_id = payment_form.cleaned_data.get('object_id')
        monto = payment_form.cleaned_data.get('monto')
        tipo = payment_form.cleaned_data.get('tipo')

        attrs = {'content_type':content_type, 'object_id':obj_id, 'monto':monto, 'tipo':tipo}

        new_payment = Payments(**attrs)
        new_payment.save()

        return redirect(purchase.get_absolute_url())

    if self_check_form.is_valid():
        content_type = self_check_form.cleaned_data.get('content_type')
        obj_id = self_check_form.cleaned_data.get('object_id')
        fecha_pago = self_check_form.cleaned_data.get('fecha_pago')
        banco_emision = self_check_form.cleaned_data.get('banco_emision')
        numero_cheque = self_check_form.cleaned_data.get('numero_cheque')
        titular_cheque = self_check_form.cleaned_data.get('titular_cheque')
        monto = self_check_form.cleaned_data.get('monto')

        cliente = purchase.client
        descripcion = purchase

        attrs = {'content_type':content_type, 'object_id':obj_id, 
                                                'cliente':cliente,
                                                'descripcion':descripcion,
                                                'fecha_pago':fecha_pago, 
                                                'banco_emision':banco_emision,
                                                'numero_cheque':numero_cheque,
                                                'titular_cheque':titular_cheque,
                                                'monto':monto,
                                                    }
        
        new_self_check = SelfChecks(**attrs)
        new_self_check.save()

        return redirect(purchase.get_absolute_url())

    if endorsed_checks_form.is_valid() and request.POST.get("check_id"):
        third_p_check = ThirdPartyChecks.objects.get(pk=int(request.POST.get("check_id")))

        content_type = endorsed_checks_form.cleaned_data.get('content_type')
        obj_id = endorsed_checks_form.cleaned_data.get('object_id')
        fecha_deposito = third_p_check.fecha_deposito
        banco_emision = third_p_check.banco_emision
        numero_cheque = third_p_check.numero_cheque
        titular_cheque = third_p_check.titular_cheque
        monto = third_p_check.monto
        cliente = third_p_check.cliente
        descripcion = third_p_check.descripcion
        observacion = '' 
        third_p_id = third_p_check.id   

        attrs = {'content_type':content_type, 'object_id':obj_id,
                                     'cliente':cliente,
                                     'descripcion': descripcion,                                      
                                     'fecha_deposito':fecha_deposito,
                                     'banco_emision':banco_emision,
                                     'numero_cheque':numero_cheque,
                                     'titular_cheque':titular_cheque,
                                     'monto':monto,
                                     'observacion':observacion,    
                                     'third_p_id':third_p_id,
                                     }

        new_endorsed_check = EndorsedChecks(**attrs)
        new_endorsed_check.save()

        third_p_check.estado = 'endosado'
        third_p_check.save()

        return redirect(purchase.get_absolute_url())

    purchase_zip = zip(animals,kg_totales,sub_totals,animal_ivas,animal_totals)

    money_zip = zip(payments,self_checks)

    return render(request, 'purchases/purchase_detail.html',
                                    {'purchase' : purchase,
                                    'kg_neto': kg_neto,
                                    'kg_cabeza':kg_cabeza,
                                    'animal_cantidades':animal_precio_kg,
                                    'total_cabezas':total_cabezas,
                                    'total_sub_totals':total_sub_totals,
                                    'total_ivas':total_ivas,
                                    'purchase_total':purchase_total,
                                    'total_kg_total':total_kg_total,
                                    'payment_form':payment_form,
                                    'payments':payments,
                                    'self_checks':self_checks,
                                    'self_check_form':self_check_form,
                                    'purchase_zip':purchase_zip,
                                    'money_zip':money_zip,
                                    'third_p_checks':third_p_checks,
                                    'endorsed_checks_form':endorsed_checks_form,
                                    'endorsed_checks':endorsed_checks
                                    })

@login_required
def purchase_create(request):
    purchase_form = PurchaseForm(request.POST or None)
    qs = Animal.objects.none()
    AnimalFormset = modelformset_factory(Animal, form=AnimalForm, extra=3)
    formset = AnimalFormset(request.POST or None, queryset=qs)

    if all([purchase_form.is_valid(),formset.is_valid()]):
        parent = purchase_form.save(commit=False)
        parent.save()

        for form in formset:
            child = form.save(commit=False)
            child.purchase = parent
            child.save()
        
        return redirect(parent.get_absolute_url())

    return render(request, 'purchases/purchases_form.html',{
                                                    'purchase_form':purchase_form,
                                                    'formset':formset,
                                                    })
                                                
