from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from payments.models import ThirdPartyChecks
from sales.models import SaleRow, Sales
from .forms import SaleSearchForm, SaleForm, SaleRowForm, SaleRowFormset
from django.contrib.postgres.search import SearchVector
from django.views.generic.edit import CreateView
from django.db import transaction
from payments.forms import PaymentForm, ThirdPartyChecksForm
from .models import Payments


@login_required
def sales_list(request):
    sales = Sales.objects.all()
    total_sales = sales.count()

    unpayed_sales = Sales.objects.filter(status = 'por cobrar')
    total_unpayed_sales = unpayed_sales.count()

    amount_to_receive_total=[]
    for sale in unpayed_sales:
        amount_to_receive = sale.calculate_amount_to_pay()
        amount_to_receive_total.append(amount_to_receive)

    amount_to_receive_total = sum(amount_to_receive_total)

    return render(request, 'sales/sales_list.html', 
                                    {'sales' : sales,
                                    'total_sales':total_sales,
                                    'total_unpayed_sales':total_unpayed_sales,
                                    'amount_to_receive_total':amount_to_receive_total,
                                    })

@login_required
def sale_search(request):
    form = SaleSearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SaleSearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Sales.objects.annotate(search=SearchVector('client','date'),).filter(search=query)
    return render(request, 'sales/search.html', {'form':form,
                                                            'query':query,
                                                            'results':results}) 


@login_required
def sales_detail(request, year, month, day, sale):
    sale = get_object_or_404(Sales, slug=sale,
                                                date__year = year,
                                                date__month = month,
                                                date__day = day )
    
    kg_neto =  sale.brute_kg - (sale.brute_kg * (sale.desbaste/100)) 

    try:   
        kg_cabeza = kg_neto / sale.total_animals
    except ZeroDivisionError:
        kg_cabeza = 0

    sale_rows = sale.salerow_set.all()

    kg_totales=[]
    for row in sale_rows:
        kg_totales.append(row.cantidad * kg_cabeza)

    animal_cabezas = list(map(int,sale_rows.values_list('cantidad', flat=True)))

    animal_precio_kg =list(map(int,sale_rows.values_list('precio_por_kg', flat=True)))

    sub_totals= [a * b for a, b in zip(animal_precio_kg, kg_totales)]

    animal_ivas = list(map(int,sale_rows.values_list('iva', flat=True)))

    animal_totals = [a + b for a, b in zip(animal_ivas, sub_totals)]

    total_sub_totals = sum(sub_totals)

    total_cabezas = sum(animal_cabezas)

    total_ivas = sum(animal_ivas)

    sale_total = sum(animal_totals)

    total_kg_total = sum(kg_totales)

    #PAGOS

    payments = sale.payments

    third_p_checks = sale.third_party_checks

    total_payments_payed = sum(list(map(int,payments.values_list('monto', flat=True))))
    total_checks_payed = sum(list(map(int,third_p_checks.values_list('monto', flat=True))))

    total_payed = total_payments_payed + total_checks_payed

    if sale_total - total_payed <=0:
        sale.change_status('cobrado')
        sale.save()


    initial_payment_data = {
        'content_type': sale.get_content_type,
        'object_id': sale.id,
    }

    payment_form = PaymentForm(request.POST or None, initial= initial_payment_data)

    third_p_form = ThirdPartyChecksForm(request.POST or None, initial= initial_payment_data)

    if payment_form.is_valid():
        content_type = payment_form.cleaned_data.get('content_type')
        obj_id = payment_form.cleaned_data.get('object_id')
        monto = payment_form.cleaned_data.get('monto')
        tipo = payment_form.cleaned_data.get('tipo')

        attrs = {'content_type':content_type, 'object_id':obj_id, 'monto':monto, 'tipo':tipo}

        new_payment = Payments(**attrs)
        new_payment.save()
        
        return redirect(sale.get_absolute_url())
    
    if third_p_form.is_valid():
        content_type = third_p_form.cleaned_data.get('content_type')
        obj_id = third_p_form.cleaned_data.get('object_id')
        fecha_deposito = third_p_form.cleaned_data.get('fecha_deposito')
        banco_emision = third_p_form.cleaned_data.get('banco_emision')
        numero_cheque = third_p_form.cleaned_data.get('numero_cheque')
        titular_cheque = third_p_form.cleaned_data.get('titular_cheque')
        monto = third_p_form.cleaned_data.get('monto')
        observacion = ''

        cliente = sale.client
        descripcion = sale
        attrs = {'content_type':content_type, 'object_id':obj_id,
                                     'cliente':cliente,
                                     'descripcion': descripcion,                                      
                                     'fecha_deposito':fecha_deposito,
                                     'banco_emision':banco_emision,
                                     'numero_cheque':numero_cheque,
                                     'titular_cheque':titular_cheque,
                                     'monto':monto,
                                     'observacion':observacion,    
                                     }

        new_third_p_check = ThirdPartyChecks(**attrs)
        new_third_p_check.save()
        
        return redirect(sale.get_absolute_url())

    sale_zip = zip(sale_rows,kg_totales,sub_totals,animal_ivas,animal_totals)
    money_zip = zip(payments,third_p_checks)

    return render(request, 'sales/sales_detail.html',
                                    {'sale' : sale,
                                    'kg_neto': kg_neto,
                                    'kg_cabeza':kg_cabeza,
                                    'animal_cantidades':animal_precio_kg,
                                    'total_cabezas':total_cabezas,
                                    'total_sub_totals':total_sub_totals,
                                    'total_ivas':total_ivas,
                                    'sale_total':sale_total,
                                    'total_kg_total':total_kg_total,
                                    'payment_form':payment_form,
                                    'third_p_form':third_p_form,
                                    'payments':payments,
                                    'third_p_checks':third_p_checks,
                                    'sale_zip' : sale_zip,
                                    'money_zip': money_zip})


class SaleCreate(CreateView):
    model = Sales
    fields = ['client', 'total_animals', 'brute_kg', 'desbaste']


class SaleAnimalsCreate(CreateView):
    model = Sales
    fields = ['client', 'total_animals', 'brute_kg', 'desbaste']

    def get_context_data(self, **kwargs):
        data = super(SaleAnimalsCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['animals'] = SaleRowFormset(self.request.POST)
        else:
            data['animals'] = SaleRowFormset()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        animals = context['animals']
        with transaction.atomic():
            self.object = form.save()
        
            if animals.is_valid():
                animals.instance = self.object
                animals.save()
        return super(SaleAnimalsCreate, self).form_valid(form)                                                                                              