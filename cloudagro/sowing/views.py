from functools import reduce
from operator import attrgetter
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from .models import Applications, Labors, SowingPurchases
from .forms import SowingPurchasesForm, ApplicationForm, LoteForm, LaborsForm
from land .models import Campaign, Lote
from payments.models import EndorsedChecks, SelfChecks, Payments, ThirdPartyChecks
from payments.forms import PaymentForm, SelfChecksForm, EndorsedChecksForm
from django.contrib.auth.decorators import login_required

@login_required
def sowing_purchases_list(request):

    campaña = Campaign.objects.filter(estado = 'vigente').first()
    
    sowing_purchases = SowingPurchases.objects.filter(campaña = campaña)

    total_purchases = sowing_purchases.count()

    unpayed_purchases = sowing_purchases.filter(estado='por pagar')

    total_unpayed_purchases = unpayed_purchases.count()

    total_amounts_to_pay = []
    for purchase in unpayed_purchases:
        unpayed_amount = int(purchase.calculate_amount_to_pay())
        total_amounts_to_pay.append(unpayed_amount)

    total_amount_to_pay = sum(total_amounts_to_pay)

    return render(request, 'sowing/sowing_purchases_list.html', {
                                                                'campaña':campaña,
                                                                'sowing_purchases':sowing_purchases,
                                                                'total_purchases':total_purchases,
                                                                'total_unpayed_purchases':total_unpayed_purchases,
                                                                'total_amount_to_pay':total_amount_to_pay,
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
            precio_lt_kg_usd = sowing_p_form.cleaned_data.get('precio_lt_kg_usd')
            lt_kg = sowing_p_form.cleaned_data.get('lt_kg')
            tipo_cambio = sowing_p_form.cleaned_data.get('tipo_cambio')
            iva = sowing_p_form.cleaned_data.get('iva')

            campaña = Campaign.objects.filter(estado = 'vigente').first()

            attrs = {'campaña':campaña,'campo':campo, 
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
def sowing_purchase_detail(request, year, month, day, sowing_purchase):

    sowing_purchase = get_object_or_404(SowingPurchases, slug=sowing_purchase,
                                                            date__year = year,
                                                            date__month = month,
                                                            date__day = day
                                                            )


    precio_lt_kg = sowing_purchase.precio_lt_kg_usd * sowing_purchase.tipo_cambio

    sub_total_usd = sowing_purchase.precio_lt_kg_usd * sowing_purchase.lt_kg

    total_usd = sub_total_usd + (sub_total_usd * (sowing_purchase.iva/100))

    payments = sowing_purchase.payments

    self_checks = sowing_purchase.self_checks

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
        sowing_purchase.estado = 'pagado'
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
                                                                })                                


@login_required
def products_averages(request):

    campaña = Campaign.objects.filter(estado = 'vigente').first()

    product_dict = SowingPurchases.calculate_averages()[0]
    
    return render(request, 'sowing/product_averages.html',{ 
                                                            'product_dict':product_dict,
                                                            'campaña':campaña,
                                                            })

@login_required
def lotes_list(request):
    
    campaña = Campaign.objects.filter(estado = 'vigente').first()

    lotes = Lote.objects.filter(campaña=campaña)

    return render(request,'sowing/lotes_list.html',{
                                                    'lotes':lotes,
                                                    'campaña':campaña
                                                })

@login_required
def lote_create(request):

    if request.method == 'POST':
        lote_form = LoteForm(data=request.POST)

        if lote_form.is_valid():

            campo = lote_form.cleaned_data.get('campo')
            numero = lote_form.cleaned_data.get('numero')
            hectareas= lote_form.cleaned_data.get('hectareas')
            tipo= lote_form.cleaned_data.get('tipo')

            campaña = Campaign.objects.filter(estado = 'vigente').first()
            
            attrs = {'campo':campo, 'numero':numero,
                    'hectareas':hectareas, 'tipo':tipo,
                    'campaña':campaña }

            new_lote = Lote(**attrs)
            new_lote.save()
        

            return redirect('sowing:lotes_list')
        
    else:
        lote_form = LoteForm()

    return render(request, 'sowing/lote_create.html',{
                                                    'lote_form':lote_form,
                                                    })

@login_required
def lote_detail(request,  lote_id):

    lote = get_object_or_404(Lote, pk=lote_id)

    product_choices = SowingPurchases.calculate_averages()[1]

    product_choices = tuple(tuple(product) for product in product_choices)

    product_averages = SowingPurchases.calculate_averages()[0]

    lote_view = request.get_full_path()

    if request.method == 'POST':
        application_form = ApplicationForm(data=request.POST)
        labors_form = LaborsForm(data=request.POST)

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

    
    else:
        application_form = ApplicationForm()
        labors_form = LaborsForm()
    
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
                                                        })