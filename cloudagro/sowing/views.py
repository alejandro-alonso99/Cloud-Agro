
from django.shortcuts import get_object_or_404, render, redirect
from land.models import Land
from harvest.models import Harvest
from .models import Applications, Labors, SowingPurchases
from .forms import SowingPurchasesForm, ApplicationForm, LoteForm, LaborsForm
from land .models import Campaign, Lote
from payments.models import EndorsedChecks, SelfChecks, Payments, ThirdPartyChecks
from payments.forms import PaymentForm, SelfChecksForm, EndorsedChecksForm
from django.contrib.auth.decorators import login_required
from purchases.forms import SearchForm, DateForm
from django.contrib.postgres.search import SearchVector
from harvest.forms import HarvestForm
from payments.forms import ChangeStateForm, DestroyObjectForm
from .forms import ChooseCampoForm, LoteNumberForm


@login_required
def sowing_purchases_list(request):
    
    search_form = SearchForm()

    date_form = DateForm()

    query = None

    date_query_start = None
    date_query_end = None

    if 'campaign' in request.session:
        campana = Campaign.objects.get(nombre=request.session['campaign']) 
    elif Campaign.objects.all():
        campana = Campaign.objects.all()[0]

    
    sowing_purchases = SowingPurchases.objects.filter(campaña = campana)

    total_purchases = sowing_purchases.count()

    unpayed_purchases = sowing_purchases.filter(status='por pagar')

    total_unpayed_purchases = unpayed_purchases.count()

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            sowing_purchases = sowing_purchases.annotate(search=SearchVector('proveedor'),).filter(search=query)
        
    if 'date_query_start' and 'date_query_end' in request.GET:
        form = DateForm(request.GET)
        if form.is_valid():
            date_query_start = form.cleaned_data['date_query_start'].strftime("%Y-%m-%d")
            date_query_end = form.cleaned_data['date_query_end'].strftime("%Y-%m-%d")
            sowing_purchases = sowing_purchases.filter(date__range=[date_query_start, date_query_end])
        

    total_amounts_to_pay = []
    for purchase in unpayed_purchases:
        unpayed_amount = int(purchase.calculate_amount_to_pay())
        total_amounts_to_pay.append(unpayed_amount)

    total_amount_to_pay = sum(total_amounts_to_pay)

    return render(request, 'sowing/sowing_purchases_list.html', {
                                                                'campaña':campana,
                                                                'sowing_purchases':sowing_purchases,
                                                                'total_purchases':total_purchases,
                                                                'total_unpayed_purchases':total_unpayed_purchases,
                                                                'total_amount_to_pay':total_amount_to_pay,
                                                                'search_form':search_form,
                                                                'query':query,
                                                                'date_form':date_form,
                                                                'date_query_start':date_query_start,
                                                                'date_query_end':date_query_end,
                                                                })


@login_required
def sowing_purchases_create(request):

    if request.method == 'POST':
        sowing_p_form = SowingPurchasesForm(data=request.POST)

        if sowing_p_form.is_valid():
            campo = sowing_p_form.cleaned_data.get('campo')
            factura = sowing_p_form.cleaned_data.get('factura')
            proveedor = sowing_p_form.cleaned_data.get('proveedor')
            producto = sowing_p_form.cleaned_data.get('producto')
            producto = producto.lower()
            precio_lt_kg_usd = sowing_p_form.cleaned_data.get('precio_lt_kg_usd')
            lt_kg = sowing_p_form.cleaned_data.get('lt_kg')
            tipo_cambio = sowing_p_form.cleaned_data.get('tipo_cambio')
            iva = sowing_p_form.cleaned_data.get('iva')

            if 'campaign' in request.session:
                campana = Campaign.objects.get(nombre=request.session['campaign']) 
            elif Campaign.objects.all():
                campana = Campaign.objects.all()[0]

            attrs = {'campaña':campana,'campo':campo, 
                                        'factura':factura,
                                        'proveedor':proveedor,
                                        'producto':producto,
                                        'precio_lt_kg_usd':precio_lt_kg_usd,
                                        'lt_kg':lt_kg,
                                        'tipo_cambio':tipo_cambio,
                                        'iva':iva,}

            new_sowing_purchase = SowingPurchases(**attrs)
            new_sowing_purchase.save()

        return redirect('sowing:sowing_purchases_list')
        
    else:
        sowing_p_form = SowingPurchasesForm()


    return render(request,'sowing/sowing_purchases_create.html',{
                                                                'sowing_p_form':sowing_p_form,
                                                                    })

@login_required
def sowing_purchase_detail(request, id):

    sowing_purchase = get_object_or_404(SowingPurchases, id=id)

    precio_lt_kg = sowing_purchase.precio_lt_kg_usd * sowing_purchase.tipo_cambio

    sub_total_usd = sowing_purchase.precio_lt_kg_usd * sowing_purchase.lt_kg

    total_usd = sub_total_usd + (sub_total_usd * (sowing_purchase.iva/100))

    payments = sowing_purchase.payments

    self_checks = sowing_purchase.self_checks

    self_checks = [check for check in self_checks if check.estado != 'anulado']

    endorsed_checks = sowing_purchase.endorsed_checks

    third_p_checks = ThirdPartyChecks.objects.filter(estado='a depositar')

    initial_payment_data = {
        'content_type': sowing_purchase.get_content_type,
        'object_id': sowing_purchase.id,
    }

    payment_form = PaymentForm(request.POST or None, initial= initial_payment_data)

    self_check_form =SelfChecksForm(request.POST or None, initial=initial_payment_data)

    endorsed_checks_form = EndorsedChecksForm(request.POST or None, initial=initial_payment_data)

    if sowing_purchase.calculate_amount_to_pay() <= 0:
        sowing_purchase.status = 'pagado'
        sowing_purchase.save()
    

    if payment_form.is_valid():
        content_type = payment_form.cleaned_data.get('content_type')
        obj_id = payment_form.cleaned_data.get('object_id')
        monto = payment_form.cleaned_data.get('monto')
        tipo = payment_form.cleaned_data.get('tipo')

        attrs = {'content_type':content_type, 'object_id':obj_id, 'monto':monto, 'tipo':tipo}

        new_payment = Payments(**attrs)
        new_payment.save()

        return redirect(sowing_purchase.get_absolute_url())

    if self_check_form.is_valid():
        content_type = self_check_form.cleaned_data.get('content_type')
        obj_id = self_check_form.cleaned_data.get('object_id')
        fecha_pago = self_check_form.cleaned_data.get('fecha_pago')
        banco_emision = self_check_form.cleaned_data.get('banco_emision')
        numero_cheque = self_check_form.cleaned_data.get('numero_cheque')
        titular_cheque = self_check_form.cleaned_data.get('titular_cheque')
        monto = self_check_form.cleaned_data.get('monto')

        cliente = sowing_purchase.proveedor
        descripcion = sowing_purchase

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

        return redirect(sowing_purchase.get_absolute_url())

    
    if endorsed_checks_form.is_valid() and request.POST.get("check_id"):
        third_p_check = ThirdPartyChecks.objects.get(pk=int(request.POST.get("check_id")))
        print(third_p_check)

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

        return redirect(sowing_purchase.get_absolute_url())

    if request.method == 'POST':
        destroy_object_form = DestroyObjectForm(data=request.POST)
        if destroy_object_form.is_valid() and request.POST.get('delete_token'):

            for check in endorsed_checks:
                check_id = check.third_p_id
                third_p_check = ThirdPartyChecks.objects.get(id=check_id)
                third_p_check.estado = 'a depositar'
                third_p_check.save()
                check.delete()

            for check in self_checks:
                check.delete()

            for payment in payments:
                payment.delete()

            sowing_purchase.delete()
            return redirect('sowing:sowing_purchases_list')
    else:
        destroy_object_form = DestroyObjectForm()


    return render(request, 'sowing/sowing_purchase_detail.html', {
                                                                'sowing_purchase':sowing_purchase,
                                                                'precio_lt_kg':precio_lt_kg,
                                                                'sub_total_usd':sub_total_usd,
                                                                'total_usd':total_usd,
                                                                'payment_form':payment_form,
                                                                'payments':payments,
                                                                'self_checks':self_checks,
                                                                'self_check_form':self_check_form,
                                                                'third_p_checks':third_p_checks,
                                                                'endorsed_checks_form':endorsed_checks_form,
                                                                'endorsed_checks':endorsed_checks,
                                                                'destroy_object_form':destroy_object_form,
                                                                })                                


@login_required
def sowing_purchase_update(request, id):

    sowing_purchase = get_object_or_404(SowingPurchases, id=id)

    if request.method == 'POST':
        sowing_p_form = SowingPurchasesForm(data=request.POST)

        if sowing_p_form.is_valid():

            payments = sowing_purchase.payments

            self_checks = sowing_purchase.self_checks

            endorsed_checks = sowing_purchase.endorsed_checks

            for check in endorsed_checks:
                    check_id = check.third_p_id
                    third_p_check = ThirdPartyChecks.objects.get(id=check_id)
                    third_p_check.estado = 'a depositar'
                    third_p_check.save()
                    check.delete()

            for check in self_checks:
                check.delete()

            for payment in payments:
                payment.delete()

            campo = sowing_p_form.cleaned_data.get('campo')
            factura = sowing_p_form.cleaned_data.get('factura')
            proveedor = sowing_p_form.cleaned_data.get('proveedor')
            producto = sowing_p_form.cleaned_data.get('producto')
            precio_lt_kg_usd = sowing_p_form.cleaned_data.get('precio_lt_kg_usd')
            lt_kg = sowing_p_form.cleaned_data.get('lt_kg')
            tipo_cambio = sowing_p_form.cleaned_data.get('tipo_cambio')
            iva = sowing_p_form.cleaned_data.get('iva')

            date = sowing_purchase.date
            if 'campaign' in request.session:
                campana = Campaign.objects.get(nombre=request.session['campaign']) 
            elif Campaign.objects.all():
                campana = Campaign.objects.all()[0]

            attrs = {'campaña':campana,'campo':campo, 
                                        'factura':factura,
                                        'proveedor':proveedor,
                                        'producto':producto,
                                        'precio_lt_kg_usd':precio_lt_kg_usd,
                                        'lt_kg':lt_kg,
                                        'tipo_cambio':tipo_cambio,
                                        'iva':iva,
                                        'date':date}

            sowing_purchase = SowingPurchases(id=id,**attrs)
            sowing_purchase.save()

        return redirect('sowing:sowing_purchases_list')
        
    else:
        sowing_p_form = SowingPurchasesForm()

    return render(request,'sowing/sowing_purchase_update.html',{'sowing_p_form':sowing_p_form})

@login_required
def products_averages(request):

    if 'campaign' in request.session:
        campana = Campaign.objects.get(nombre=request.session['campaign']) 
    elif Campaign.objects.all():
        campana = Campaign.objects.all()[0]

    product_dict = SowingPurchases.calculate_averages(campana)[0]
    
    return render(request, 'sowing/product_averages.html',{ 
                                                            'product_dict':product_dict,
                                                            'campaña':campana,
                                                            })

@login_required
def lotes_list(request):
    if 'campaign' in request.session:
        campana = Campaign.objects.get(nombre=request.session['campaign']) 
    elif Campaign.objects.all():
        campana = Campaign.objects.all()[0]

    lotes = Lote.objects.filter(campaña=campana)

    search_form = SearchForm()

    campo_form = ChooseCampoForm()

    number_form = LoteNumberForm()

    query = None

    campo = None

    number_query = None

    if 'number_query' in request.GET:
        form = LoteNumberForm(request.GET)
        if form.is_valid():
            number_query = int(form.cleaned_data['number_query'])
            lotes = lotes.filter(numero = number_query)

    if 'campo' in request.GET:
        form = ChooseCampoForm(request.GET)
        if form.is_valid():
            campo = str(form.cleaned_data['campo'])
            campo = campo.capitalize()
            campo_query = Land.objects.filter(nombre=campo).first()
            lotes = lotes.filter(campo=campo_query)

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            lotes = lotes.annotate(search=SearchVector('tipo'),).filter(search=query)



    return render(request,'sowing/lotes_list.html',{
                                                    'lotes':lotes,
                                                    'campaña':campana,
                                                    'search_form':search_form,
                                                    'query':query,
                                                    'campo_form':campo_form,
                                                    'campo':campo,
                                                    'number_form':number_form,
                                                    'number_query':number_query,
                                                })

@login_required
def lote_create(request):

    if 'campaign' in request.session:
        campana = Campaign.objects.get(nombre=request.session['campaign']) 
    elif Campaign.objects.all():
        campana = Campaign.objects.all()[0]

    if request.method == 'POST':
        lote_form = LoteForm(request.POST, campana=campana)

        if lote_form.is_valid():

            campo = lote_form.cleaned_data.get('campo')
            numero = lote_form.cleaned_data.get('numero')
            hectareas= lote_form.cleaned_data.get('hectareas')
            tipo= lote_form.cleaned_data.get('tipo')
            
            attrs = {'campo':campo, 'numero':numero,
                    'hectareas':hectareas, 'tipo':tipo,
                    'campaña':campana }

            new_lote = Lote(**attrs)
            new_lote.save()
        

            return redirect('sowing:lotes_list')
        
    else:
        lote_form = LoteForm(campana=campana)

    return render(request, 'sowing/lote_create.html',{
                                                    'lote_form':lote_form,
                                                    })

@login_required
def lote_detail(request,  lote_id):

    if 'campaign' in request.session:
        campana = Campaign.objects.get(nombre=request.session['campaign']) 
    elif Campaign.objects.all():
        campana = Campaign.objects.all()[0]

    lote = get_object_or_404(Lote, pk=lote_id)

    product_choices = SowingPurchases.calculate_averages(campana)[1]

    product_choices = tuple(tuple(product) for product in product_choices)

    product_averages = SowingPurchases.calculate_averages(campana)[0]

    lote_view = request.get_full_path()

    if request.method == 'POST':
        application_form = ApplicationForm(data=request.POST)
        labors_form = LaborsForm(data=request.POST)
        harvest_form = HarvestForm(data=request.POST)
        change_state_form = ChangeStateForm(data=request.POST)
        destroy_object_form = DestroyObjectForm(data=request.POST)

        if application_form.is_valid():
            
            numero = application_form.cleaned_data.get('numero')
            lt_kg = application_form.cleaned_data.get('lt_kg')
            producto = application_form.cleaned_data.get('producto')
            tipo = application_form.cleaned_data.get('tipo')

            attrs = {'numero':numero, 'lt_kg':lt_kg,
                        'producto':producto, 'lote':lote, 'tipo':tipo}

            new_application = Applications(**attrs)
            new_application.save()

            return redirect(lote_view)
        
        if labors_form.is_valid():
            numero = labors_form.cleaned_data.get('numero')
            costo_ha = labors_form.cleaned_data.get('costo_ha')
            nombre = labors_form.cleaned_data.get('nombre').lower()

            attrs = {'numero':numero, 'costo_ha':costo_ha, 'nombre':nombre, 
                        'lote':lote}
            
            new_labor = Labors(**attrs)
            new_labor.save()
            
            return redirect(lote_view)

        if harvest_form.is_valid():
            kg_totales = harvest_form.cleaned_data.get('kg_totales')
            attrs = {'kg_totales':kg_totales, 'lote':lote}
            new_harvest = Harvest(**attrs)
            new_harvest.save()
            lote.estado = 'cosechado'
            lote.save()

            return redirect(lote_view)

        
        if change_state_form.is_valid() and request.POST.get('change_state_token'):            
            cosecha = Harvest.objects.filter(lote=lote)
            cosecha.delete()
            lote.estado = 'no cosechado'
            lote.save()

            return redirect(lote_view)
        
        if destroy_object_form.is_valid() and request.POST.get('delete_token'):
            lote.delete()
            return redirect('sowing:lotes_list')

    else:
        application_form = ApplicationForm()
        labors_form = LaborsForm()
        harvest_form = HarvestForm()
        change_state_form = ChangeStateForm()
        destroy_object_form = DestroyObjectForm()
    
    applications = lote.applications_set.all()

    application_numbers = list(map(int,applications.values_list('numero', flat=True)))
    
    applications_dict = {}
    for number in application_numbers:
        applications_dict[number] = {}
        number_x_applications = applications.filter(numero=number)
        for application in number_x_applications:
            applications_dict[number][application] = []
            applications_dict[number][application].append(application.calculate_sub_total(product_averages)[0])
            applications_dict[number][application].append(application.calculate_sub_total(product_averages)[1])

    application_totals_by_type = {}
    applicaton_types = list(map(str,applications.values_list('tipo', flat=True)))
    for type in applicaton_types:
        type_applications = applications.filter(tipo=type)
        type_total = 0

        for application in type_applications:
            application_sub_total = float(application.calculate_sub_total(product_averages)[0])
            type_total = type_total + application_sub_total
        
    
        application_totals_by_type[type] = type_total
    
    applications_total = sum(application_totals_by_type.values())

    labors = lote.labors_set.all()
    labors_numbers = list(map(int,labors.values_list('numero', flat=True)))
    labors_dict = {}
    for number in labors_numbers:
        labors_dict[number] = {}
        number_x_labors = labors.filter(numero=number)
        for labor in number_x_labors:
            labors_dict[number][labor] = labor.calculate_sub_total()

    labors_totals_by_type = {}
    labors_types = list(map(str,labors.values_list('nombre', flat=True)))
    for type in labors_types:
        type_labors = labors.filter(nombre=type)
        type_total = 0

        for labor in type_labors:
            labor_sub_total = float(labor.calculate_sub_total())
            type_total = type_total + labor_sub_total
        
    
        labors_totals_by_type[type] = type_total

    labors_total = sum(labors_totals_by_type.values())

    lote_total = applications_total + labors_total

    if lote.estado == 'cosechado':
        cosecha = Harvest.objects.filter(lote=lote).first()
        kg_totales = cosecha.kg_totales
        quintales_ha = (kg_totales/lote.hectareas)/100
    else:
        kg_totales = None
        quintales_ha = None

    sowing_purchases = SowingPurchases.objects.all()

    products = sowing_purchases.values_list('producto',flat=True)
    return render(request, 'sowing/lote_detail.html', {
                                                        'lote':lote,
                                                        'application_form':application_form,
                                                        'applications_dict':applications_dict,
                                                        'application_totals_by_type':application_totals_by_type,
                                                        'labors_form':labors_form,
                                                        'labors':labors,
                                                        'labors_dict':labors_dict,
                                                        'labors_totals_by_type':labors_totals_by_type,
                                                        'applications_total':applications_total,
                                                        'labors_total': labors_total,
                                                        'lote_total':lote_total,
                                                        'harvest_form': harvest_form,
                                                        'change_state_form':change_state_form,
                                                        'kg_totales':kg_totales,
                                                        'quintales_ha':quintales_ha,
                                                        'destroy_object_form':destroy_object_form,
                                                        'products':products,
                                                        })

@login_required
def lote_update(request, id):

    lote = get_object_or_404(Lote, id=id)

    if request.method == 'POST':
        lote_form = LoteForm(data=request.POST)

        if lote_form.is_valid():

            campo = lote_form.cleaned_data.get('campo')
            numero = lote_form.cleaned_data.get('numero')
            hectareas= lote_form.cleaned_data.get('hectareas')
            tipo= lote_form.cleaned_data.get('tipo')

            if 'campaign' in request.session:
                campana = Campaign.objects.get(nombre=request.session['campaign']) 
            elif Campaign.objects.all():
                campana = Campaign.objects.all()[0]
            
            attrs = {'campo':campo, 'numero':numero,
                    'hectareas':hectareas, 'tipo':tipo,
                    'campaña':campana }


            lote = Lote(id=id, **attrs)
            lote.save()
        

            return redirect(lote.get_absolute_url())
        
    else:
        lote_form = LoteForm()

    return render(request, 'sowing/lote_update.html',{
                                                        'lote':lote,
                                                        'lote_form':lote_form,
                                                    })

@login_required                                       
def application_detail(request,id):

    application = get_object_or_404(Applications, id=id)

    lote = application.lote

    if request.method == 'POST':
        destroy_object_form = DestroyObjectForm(data=request.POST)
        if destroy_object_form.is_valid() and request.POST.get('delete_token'):
            application.delete()
            return redirect(lote.get_absolute_url())

    else:
        destroy_object_form = DestroyObjectForm()

    return render(request, 'sowing/application_detail.html',{
                                                            'application':application,
                                                            'destroy_object_form':destroy_object_form,
                                                            })

@login_required                                       
def application_update(request,id):

    application = get_object_or_404(Applications, id=id)

    lote = application.lote

    if request.method == 'POST':
        application_form = ApplicationForm(data=request.POST)

        if application_form.is_valid():

            numero = application_form.cleaned_data.get('numero')
            producto = application_form.cleaned_data.get('producto')
            lt_kg =  application_form.cleaned_data.get('lt_kg')
            tipo= application_form.cleaned_data.get('tipo')            
            
            date = application.date

            attrs = {'numero':numero, 'producto':producto,
                    'lt_kg':lt_kg, 'tipo':tipo, 'date':date,
                    'lote':lote }


            application = Applications(id=id, **attrs)
            application.save()
        

            return redirect(lote.get_absolute_url())
        
    else:
        application_form = ApplicationForm()

    return render(request, 'sowing/application_update.html',{   
                                                            'application':application,
                                                            'application_form':application_form,
                                                            }) 

@login_required                                       
def labor_detail(request, id):

    labor = get_object_or_404(Labors, id=id)

    lote = labor.lote

    if request.method == 'POST':
        destroy_object_form = DestroyObjectForm(data=request.POST)
        if destroy_object_form.is_valid() and request.POST.get('delete_token'):
            labor.delete()
            return redirect(lote.get_absolute_url())

    else:
        destroy_object_form = DestroyObjectForm()

    return render(request, 'sowing/labor_detail.html',{
                                                        'labor':labor,
                                                        'destroy_object_form':destroy_object_form,
                                                        })

@login_required                                       
def labor_update(request, id):

    labor = get_object_or_404(Labors, id=id)

    lote = labor.lote

    if request.method == 'POST':
        labor_form = LaborsForm(data=request.POST)

        if labor_form.is_valid():

            numero = labor_form.cleaned_data.get('numero')
            nombre = labor_form.cleaned_data.get('nombre')
            costo_ha =  labor_form.cleaned_data.get('costo_ha')
            
            date = labor.date

            attrs = {'numero':numero, 'nombre':nombre,
                    'costo_ha':costo_ha, 'date':date,
                    'lote':lote }


            labor = Labors(id=id, **attrs)
            labor.save()
        

            return redirect(lote.get_absolute_url())
        
    else:
        labor_form = LaborsForm()
    
    return render(request, 'sowing/labor_update.html', {
                                                        'labor':labor,
                                                        'labor_form':labor_form,
                                                        })