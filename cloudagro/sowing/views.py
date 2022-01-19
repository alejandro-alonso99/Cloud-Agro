from django.shortcuts import get_object_or_404, render, redirect
from .models import SowingPurchases
from .forms import SowingPurchasesForm
from land .models import Campaign
from payments.models import EndorsedChecks, SelfChecks, Payments, ThirdPartyChecks
from payments.forms import PaymentForm, SelfChecksForm, EndorsedChecksForm


def sowing_purchases_list(request):

    campaña = Campaign.objects.filter(estado = 'vigente').first()
    
    sowing_purchases = SowingPurchases.objects.filter(campaña = campaña)

    total_purchases = sowing_purchases.count()

    return render(request, 'sowing/sowing_purchases_list.html', {
                                                                'campaña':campaña,
                                                                'sowing_purchases':sowing_purchases,
                                                                'total_purchases':total_purchases,
                                                                })


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

def sowing_purchase_detail(request, year, month, day, sowing_purchase):

    sowing_purchase = get_object_or_404(SowingPurchases, slug=sowing_purchase,
                                                            date__year = year,
                                                            date__month = month,
                                                            date__day = day
                                                            )


    precio_lt_kg = sowing_purchase.precio_lt_kg_usd * sowing_purchase.tipo_cambio

    sub_total_usd = sowing_purchase.precio_lt_kg_usd * sowing_purchase.lt_kg

    total_usd = sub_total_usd + (sub_total_usd * sowing_purchase.iva)

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

    
    print(sowing_purchase.estado)

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

