from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from land.models import Campaign
from payments.models import EndorsedChecks
from payments.models import ThirdPartyChecks
from sales.models import SaleRow, Sales
from .forms import DeductionForm, GrainSaleForm, RententionForm, SaleSearchForm, SaleForm, SaleRowForm
from django.contrib.postgres.search import SearchVector
from payments.forms import PaymentForm, ThirdPartyChecksForm
from django.forms.models import modelformset_factory
from .models import Deductions, GrainSales, Payments, Retentions
from purchases.forms import SearchForm, DateForm
from payments.forms import DestroyObjectForm

@login_required
def sales_list(request):

    search_form = SearchForm()

    date_form = DateForm()

    query = None

    date_query_start = None
    date_query_end = None

    sales = Sales.objects.all()
    total_sales = sales.count()

    unpayed_sales = Sales.objects.filter(status = 'por cobrar')
    total_unpayed_sales = unpayed_sales.count()

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            sales = Sales.objects.annotate(search=SearchVector('client'),).filter(search=query)
        
    if 'date_query_start' and 'date_query_end' in request.GET:
        form = DateForm(request.GET)
        if form.is_valid():
            date_query_start = form.cleaned_data['date_query_start'].strftime("%Y-%m-%d")
            date_query_end = form.cleaned_data['date_query_end'].strftime("%Y-%m-%d")
            sales = Sales.objects.filter(date__range=[date_query_start, date_query_end])

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
                                    'search_form':search_form,
                                    'query':query,
                                    'date_form':date_form,
                                    'date_query_start':date_query_start,
                                    'date_query_end':date_query_end,
                                    })


@login_required
def sales_detail(request, id):
    sale = get_object_or_404(Sales, id=id)
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

    if request.method == 'POST':
        destroy_object_form = DestroyObjectForm(data=request.POST)
        if destroy_object_form.is_valid() and request.POST.get('delete_token'):

            for payment in payments:
                payment.delete()

            for check in third_p_checks:
                check_id = check.id
                if EndorsedChecks.objects.filter(third_p_id = check_id):
                    endorsed_check = EndorsedChecks.objects.filter(third_p_id = check_id).first()
                    parent = endorsed_check.content_object
                    parent.status = 'por pagar'
                    parent.save()
                    endorsed_check.delete()

                check.delete()

            sale.delete()
            return redirect('sales:sale_list')

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
                                    
@login_required
def sale_create(request):
    sale_form = SaleForm(request.POST or None)
    qs = SaleRow.objects.none()
    SaleRowFormset = modelformset_factory(SaleRow, form=SaleRowForm, extra=3)
    formset = SaleRowFormset(request.POST or None, queryset=qs)

    if all([sale_form.is_valid(),formset.is_valid()]):
        parent = sale_form.save(commit=False)
        parent.save()

        for form in formset:
            child = form.save(commit=False)
            child.sale = parent
            child.save()
            SaleRow.delete_empty()

        return redirect(parent.get_absolute_url())

    return render(request, 'sales/sales_form.html',{
                                                    'sale_form':sale_form,
                                                    'formset':formset,
                                                    })

@login_required
def sale_update(request, id):

    sale = get_object_or_404(Sales, id=id)

    sale_form = SaleForm(request.POST or None)
    qs = SaleRow.objects.none()
    SaleRowFormset = modelformset_factory(SaleRow, form=SaleRowForm, extra=3)
    formset = SaleRowFormset(request.POST or None, queryset=qs)

    if all([sale_form.is_valid(),formset.is_valid()]):
        payments = sale.payments

        for payment in payments:
            payment.delete()

        third_p_checks = sale.third_party_checks

        for check in third_p_checks:
            check_id = check.id
            if EndorsedChecks.objects.filter(third_p_id = check_id):
                endorsed_check = EndorsedChecks.objects.filter(third_p_id = check_id).first()
                parent = endorsed_check.content_object
                parent.status = 'por pagar'
                parent.save()
                endorsed_check.delete()
            
            check.delete()

        sale_rows = sale.salerow_set.all()
        for row in sale_rows:
            row.delete()

        campo = sale_form.cleaned_data.get('campo')
        client = sale_form.cleaned_data.get('client')
        brute_kg = sale_form.cleaned_data.get('brute_kg')
        desbaste = sale_form.cleaned_data.get('desbaste')
        total_animals = sale_form.cleaned_data.get('total_animals')

        date = sale.date

        attrs = {'campo':campo, 'client':client,
                    'brute_kg':brute_kg, 'desbaste':desbaste,
                    'total_animals':total_animals,
                    'date':date, 'status':'por cobrar'}

        sale = Sales(id=id, **attrs)
        sale.save()

        for form in formset:
            child = form.save(commit=False)
            child.sale = sale
            child.save()
            SaleRow.delete_empty()

        return redirect(sale.get_absolute_url())

    return render(request, 'sales/sale_update.html',{
                                                    'sale_form':sale_form,
                                                    'formset':formset,
                                                    })

@login_required
def grains_sale_create(request):

    campana = Campaign.objects.get(id=1)

    grain_sale_form = GrainSaleForm(request.POST or None)

    if grain_sale_form.is_valid():
        new_grain_sale = grain_sale_form.save(commit=False)
        new_grain_sale.campana = campana
        new_grain_sale.save()

        return render('sales:grain_sales_list')

    return render(request, 'sales/grains_sales_create.html',{
                                                            'grain_sale_form':grain_sale_form,
                                                            })
@login_required
def grains_sales_list(request):

    campana = Campaign.objects.first()

    search_form = SearchForm()

    date_form = DateForm()

    query = None

    date_query_start = None
    date_query_end = None

    grain_sales = GrainSales.objects.filter(campana=campana)

    total_sales = grain_sales.count()

    unpayed_sales = grain_sales.filter(status='por cobrar').count()


    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            grain_sales = GrainSales.objects.annotate(search=SearchVector('cliente'),).filter(search=query)
        
    if 'date_query_start' and 'date_query_end' in request.GET:
        form = DateForm(request.GET)
        if form.is_valid():
            date_query_start = form.cleaned_data['date_query_start'].strftime("%Y-%m-%d")
            date_query_end = form.cleaned_data['date_query_end'].strftime("%Y-%m-%d")
            grain_sales = GrainSales.objects.filter(fecha__range=[date_query_start, date_query_end])

    return render(request,'sales/grains_sales_list.html',{
                                                        'grain_sales':grain_sales,
                                                        'total_sales':total_sales,
                                                        'unpayed_sales':unpayed_sales,
                                                        'campana':campana,
                                                        'search_form':search_form,
                                                        'date_form':date_form,
                                                        'query':query,
                                                        'date_query_start':date_query_start,
                                                        'date_query_end':date_query_end,
                                                        })

@login_required
def grain_sale_detail(request,id):

    grain_sale = get_object_or_404(GrainSales, id=id)

    deduction_form = DeductionForm(request.POST or None)

    retention_form = RententionForm(request.POST or None)

    destroy_object_form = DestroyObjectForm(request.POST or None)

    if deduction_form.is_valid():

        new_ded = deduction_form.save(commit=False)
        new_ded.sale = grain_sale
        new_ded.save()

        return redirect(grain_sale.get_absolute_url())
    
    if retention_form.is_valid():

        new_ret = retention_form.save(commit=False)
        new_ret.sale = grain_sale
        new_ret.save()

        return redirect(grain_sale.get_absolute_url())

    
    if destroy_object_form.is_valid and request.POST.get('ded_id'):
        ded_id = int(request.POST.get("ded_id"))
        ded = Deductions.objects.get(pk=ded_id)
        ded.delete()

        return redirect(grain_sale.get_absolute_url())
    
    if destroy_object_form.is_valid and request.POST.get('ret_id'):
        ret_id = int(request.POST.get("ret_id"))
        ret = Retentions.objects.get(pk=ret_id)
        ret.delete()

        return redirect(grain_sale.get_absolute_url())
        

    return render(request, 'sales/grain_sale_detail.html',{
                                                            'grain_sale':grain_sale,
                                                            'deduction_form':deduction_form,
                                                            'retention_form':retention_form,
                                                            'destroy_object_form':destroy_object_form,
                                                            })