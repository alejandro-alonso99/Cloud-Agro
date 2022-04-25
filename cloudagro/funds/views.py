from http import client
from django.shortcuts import get_object_or_404, render, redirect
from payments.forms import ThirdPartyChecksForm
from payments.forms import SelfChecksForm
from payments.models import EndorsedChecks
from payments.models import ThirdPartyChecks, SelfChecks
from payments.forms import ChangeStateForm
from .forms import FundManualMoveForm
from .models import FundManualMove
from django.contrib.auth.decorators import login_required
from payments.forms import DestroyObjectForm
from purchases.forms import DateForm, SearchForm
from django.contrib.postgres.search import SearchVector

@login_required
def fund_manualmove_create(request):

    if request.method == 'POST':
        move_form = FundManualMoveForm(data=request.POST)
        
        if move_form.is_valid:
           move_form.save()

        return redirect('account:dashboard')
    
    else:
        move_form = FundManualMoveForm()

    last_3_manual_moves = FundManualMove.objects.all()[:3]

    return render(request, 'funds/funds_manualmove_create.html',{
                                                            'move_form': move_form,
                                                            'last_3_manual_moves':last_3_manual_moves,
                                                            })                                 

@login_required
def funds_manualmove_list(request):

    manual_moves = FundManualMove.objects.all()
    
    date_form = DateForm()

    date_query_start = None
    date_query_end = None

    if 'date_query_start' and 'date_query_end' in request.GET:
        form = DateForm(request.GET)
        if form.is_valid():
            date_query_start = form.cleaned_data['date_query_start'].strftime("%Y-%m-%d")
            date_query_end = form.cleaned_data['date_query_end'].strftime("%Y-%m-%d")
            manual_moves = manual_moves.filter(date__range=[date_query_start, date_query_end])


    return render(request, 'funds/manualmove_list.html',{
                                                        'manual_moves':manual_moves,
                                                        'date_form':date_form,
                                                        'date_query_start':date_query_start,
                                                        'date_query_end':date_query_end,                                                                                                                
                                                         })

@login_required
def funds_manualmove_detail(request, move):

    manualmove = get_object_or_404(FundManualMove, id=move)

    if request.method == 'POST':
        destroy_object_form = DestroyObjectForm(request.POST)
        manualmove.delete()

        return redirect('funds:funds_manualmoves')

    else:
        destroy_object_form = DestroyObjectForm()        

    return render(request, 'funds/manualmove_detail.html',{
                                                            'manualmove':manualmove,
                                                            'destroy_object_form':destroy_object_form,
                                                            })                                                     


@login_required
def funds_third_party_checks(request):
    third_party_checks = ThirdPartyChecks.objects.all()

    to_deposit_checks = third_party_checks.filter(estado="a depositar")

    today_checks = 0
    week_checks = 0
    two_week_checks = 0
    month_checks = 0
    two_month_checks = 0
    more_months_checks = 0

    for check in to_deposit_checks:
        remaining = check.calculate_remaining
        monto = check.monto

        if remaining <= 0:
            today_checks = today_checks + monto
        
        elif remaining <=7:
            week_checks = week_checks + monto

        elif remaining <=15:
            two_week_checks = two_week_checks + monto
        
        elif remaining <=30:
            month_checks =  month_checks + monto
        
        elif remaining <=60:
            two_month_checks = two_month_checks + monto
        
        else:
            more_months_checks = more_months_checks + monto
    
    total_to_pay_checks = today_checks + week_checks + two_week_checks + month_checks + two_month_checks + more_months_checks

    search_form = SearchForm()

    date_form = DateForm()

    query = None

    date_query_start = None
    date_query_end = None

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            third_party_checks = ThirdPartyChecks.objects.annotate(search=SearchVector('cliente'),).filter(search=query)
        
    if 'date_query_start' and 'date_query_end' in request.GET:
        form = DateForm(request.GET)
        if form.is_valid():
            date_query_start = form.cleaned_data['date_query_start'].strftime("%Y-%m-%d")
            date_query_end = form.cleaned_data['date_query_end'].strftime("%Y-%m-%d")
            third_party_checks = ThirdPartyChecks.objects.filter(fecha_ingreso__range=[date_query_start, date_query_end])

    return render(request, 'funds/funds_third_party_checks.html',{
                                                            'third_party_checks':third_party_checks,
                                                            'today_checks':today_checks,
                                                            'week_checks':week_checks,
                                                            'two_week_checks':two_week_checks,
                                                            'month_checks':month_checks,
                                                            'two_month_checks':two_month_checks,
                                                            'more_months_checks':more_months_checks,
                                                            'total_to_pay_checks':total_to_pay_checks,
                                                            'search_form':search_form,
                                                            'date_form':date_form,
                                                            'query':query,
                                                            'date_query_start':date_query_start,
                                                            'date_query_end':date_query_end,
                                                            })

@login_required
def third_p_check_detail(request, id):

    third_p_check = get_object_or_404(ThirdPartyChecks, id=id)                                                            

    
    if request.method == 'POST' and request.POST.get('change_state_token'):

        change_state_form = ChangeStateForm(request.POST)

        if change_state_form.is_valid():
            third_p_check.change_state()

            return redirect(third_p_check.get_absolute_url())
    else:
        change_state_form = ChangeStateForm()
    
    if request.method == 'POST' and request.POST.get('del_endose_token'):

        change_state_form = ChangeStateForm(request.POST)

        if change_state_form.is_valid():
            endosed_check = EndorsedChecks.objects.filter(third_p_id=third_p_check.id).first()

            endosed_parent = endosed_check.content_object

            endosed_parent.status = 'por pagar'
            endosed_parent.save()
            endosed_check.delete()

            third_p_check.estado = 'a depositar'
            third_p_check.save()

            return redirect(endosed_parent.get_absolute_url())
    else:
        change_state_form = ChangeStateForm()
    

    if request.method == 'POST' and request.POST.get("delete_token"):
        parent = third_p_check.content_object

        parent.status = 'por cobrar'
        parent.save()

        if third_p_check.estado == 'endosado':
            endosed_check = EndorsedChecks.objects.filter(third_p_id=third_p_check.id).first()

            endosed_parent = endosed_check.content_object

            endosed_parent.status = 'por pagar'
            endosed_parent.save()
            endosed_check.delete()

        destroy_object_form = DestroyObjectForm(request.POST)
        third_p_check.delete()

        return redirect(parent.get_absolute_url())

    else:
        destroy_object_form = DestroyObjectForm()

    return render(request, 'funds/third_p_check_detail.html',{
                                                        'third_p_check' : third_p_check,
                                                        #'change_state_form':change_state_form,
                                                        'destroy_object_form':destroy_object_form,
                                                            })

@login_required
def third_p_check_update(request, id):

    third_p_check = get_object_or_404(ThirdPartyChecks, id=id)

    parent = third_p_check.content_object

    parent_model = parent.__class__.__name__

    initial_payment_data = {
        'content_type': parent.get_content_type,
        'object_id': parent.id,
    }
    
    third_p_form = ThirdPartyChecksForm(request.POST or None, initial=initial_payment_data)

    if third_p_form.is_valid():
        content_type = third_p_form.cleaned_data.get('content_type')
        obj_id = third_p_form.cleaned_data.get('object_id')
        fecha_deposito = third_p_form.cleaned_data.get('fecha_deposito')
        banco_emision = third_p_form.cleaned_data.get('banco_emision')
        numero_cheque = third_p_form.cleaned_data.get('numero_cheque')
        titular_cheque = third_p_form.cleaned_data.get('titular_cheque')
        monto = third_p_form.cleaned_data.get('monto')
        observacion = ''
        fecha_ingreso = third_p_check.fecha_ingreso

        if parent_model == 'Sales':
            cliente = parent.client

        #agregar acá para ventas de granos
        observacion = ''
        descripcion = ''
        attrs = {'content_type':content_type, 'object_id':obj_id,
                                     'cliente':cliente,
                                     'descripcion': descripcion,                                      
                                     'fecha_deposito':fecha_deposito,
                                     'banco_emision':banco_emision,
                                     'numero_cheque':numero_cheque,
                                     'titular_cheque':titular_cheque,
                                     'monto':monto,
                                     'observacion':observacion,
                                     'fecha_ingreso':fecha_ingreso,    
                                     }

        third_p_check = ThirdPartyChecks(id,**attrs)
        third_p_check.save()
        
        return redirect(third_p_check.get_absolute_url())


    return render(request,'funds/third_p_check_update.html',{
                                                            'third_p_check':third_p_check,
                                                            'third_p_form': third_p_form,       
                                                            })

@login_required
def funds_self_checks(request):

    self_checks = SelfChecks.objects.all()

    to_pay_checks = self_checks.filter(estado='a pagar')

    today_checks = 0
    week_checks = 0
    two_week_checks = 0
    month_checks = 0
    two_month_checks = 0
    more_months_checks = 0

    for check in to_pay_checks:
        remaining = check.calculate_remaining
        monto = check.monto

        if remaining <= 0:
            today_checks = today_checks + monto
        
        elif remaining <=7:
            week_checks = week_checks + monto

        elif remaining <=15:
            two_week_checks = two_week_checks + monto
        
        elif remaining <=30:
            month_checks =  month_checks + monto
        
        elif remaining <=60:
            two_month_checks = two_month_checks + monto
        
        else:
            more_months_checks = more_months_checks + monto
    
    total_to_pay_checks = today_checks + week_checks + two_week_checks + month_checks + two_month_checks + more_months_checks

    search_form = SearchForm()

    date_form = DateForm()

    query = None

    date_query_start = None
    date_query_end = None

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            self_checks = SelfChecks.objects.annotate(search=SearchVector('cliente'),).filter(search=query)
        
    if 'date_query_start' and 'date_query_end' in request.GET:
        form = DateForm(request.GET)
        if form.is_valid():
            date_query_start = form.cleaned_data['date_query_start'].strftime("%Y-%m-%d")
            date_query_end = form.cleaned_data['date_query_end'].strftime("%Y-%m-%d")
            self_checks = SelfChecks.objects.filter(fecha_salida__range=[date_query_start, date_query_end])

    return render(request, 'funds/funds_self_checks.html',{
                                                            'self_checks':self_checks,
                                                            'today_checks':today_checks,
                                                            'week_checks':week_checks,
                                                            'two_week_checks':two_week_checks,
                                                            'month_checks':month_checks,
                                                            'two_month_checks':two_month_checks,
                                                            'more_months_checks':more_months_checks,
                                                            'total_to_pay_checks':total_to_pay_checks,
                                                            'search_form':search_form,
                                                            'query':query,
                                                            'date_form':date_form,
                                                            'date_query_start':date_query_start,
                                                            'date_query_end':date_query_end,
                                                            })
@login_required
def self_check_detail(request, id):

    self_check = get_object_or_404(SelfChecks, id=id)

    if request.method == 'POST' and request.POST.get("change_token"):
        change_state_form = ChangeStateForm(request.POST)

        destroy_object_form = DestroyObjectForm(request.POST)

        if change_state_form.is_valid():
            self_check.change_state()

            return redirect(self_check.get_absolute_url())
    else:
        change_state_form = ChangeStateForm()


    if request.method == 'POST' and request.POST.get("delete_token"):
        parent = self_check.content_object
        parent_model = parent.__class__.__name__
        if parent_model == 'Purchases' or parent_model == 'SowingPurchases' or parent_model == 'Expenses':
            parent.status = 'por pagar'
            parent.save()

        elif parent_model == 'Sales':
            parent.status = 'por cobrar'
            parent.save()


        destroy_object_form = DestroyObjectForm(request.POST)
        self_check.delete()

        return redirect(parent.get_absolute_url())
    
    if request.method == 'POST' and request.POST.get("cancel_token"):
        parent = self_check.content_object
        print(parent)
        parent.status = 'por pagar'
        parent.save()

        destroy_object_form = DestroyObjectForm(request.POST)
        self_check.estado = 'anulado'
        self_check.save()

        return redirect(self_check.get_absolute_url())
    
    if request.method == 'POST' and request.POST.get("del_cancel_token"):
        destroy_object_form = DestroyObjectForm(request.POST)
        self_check.estado = 'por pagar'
        self_check.save()

        return redirect(self_check.get_absolute_url())

    else:
        destroy_object_form = DestroyObjectForm()

    return render(request, 'funds/self_check_detail.html',{
                                                            'self_check':self_check,
                                                            'change_state_form':change_state_form,
                                                            'destroy_object_form':destroy_object_form,
                                                            })                                                            

@login_required
def self_check_update(request, id):

    self_check = get_object_or_404(SelfChecks, id=id)

    parent = self_check.content_object

    parent_model = parent.__class__.__name__
    
    initial_payment_data = {
        'content_type': parent.get_content_type,
        'object_id': parent.id,
    }
    
    self_check_form =SelfChecksForm(request.POST or None, initial=initial_payment_data)

    if self_check_form.is_valid():
        content_type = self_check_form.cleaned_data.get('content_type')
        obj_id = self_check_form.cleaned_data.get('object_id')
        fecha_pago = self_check_form.cleaned_data.get('fecha_pago')
        banco_emision = self_check_form.cleaned_data.get('banco_emision')
        numero_cheque = self_check_form.cleaned_data.get('numero_cheque')
        titular_cheque = self_check_form.cleaned_data.get('titular_cheque')
        monto = self_check_form.cleaned_data.get('monto')

        fecha_salida = self_check.fecha_salida

        if parent_model == 'Purchases':
            cliente = parent.client
            descripcion = parent.__str__

        elif parent_model == 'Expenses':
            cliente = parent.concepto
            descripcion = parent.descripcion
        
        else:
            cliente = parent.proveedor
            descripcion = parent.producto

        attrs = {'content_type':content_type, 'object_id':obj_id, 
                                                'cliente':cliente,
                                                'descripcion':descripcion,
                                                'fecha_pago':fecha_pago, 
                                                'banco_emision':banco_emision,
                                                'numero_cheque':numero_cheque,
                                                'titular_cheque':titular_cheque,
                                                'monto':monto,
                                                'fecha_salida':fecha_salida
                                                }
        
        self_check = SelfChecks(id,**attrs)
        self_check.save()

        return redirect(parent.get_absolute_url())

    return render(request, 'funds/self_check_update.html',{'self_check':self_check,
                                                            'self_check_form':self_check_form,    
                                                        })