from django.shortcuts import get_object_or_404, render, redirect
from payments.models import EndorsedChecks
from payments.models import ThirdPartyChecks, SelfChecks
from payments.forms import ChangeStateForm
from .forms import FundManualMoveForm
from .models import FundManualMove
from django.contrib.auth.decorators import login_required
from payments.forms import DestroyObjectForm
from purchases.forms import DateForm

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

    date_form = DateForm()

    date_query_start = None
    date_query_end = None

    manual_moves = FundManualMove.objects.all()

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

    return render(request, 'funds/funds_third_party_checks.html',{
                                                            'third_party_checks':third_party_checks,
                                                            'today_checks':today_checks,
                                                            'week_checks':week_checks,
                                                            'two_week_checks':two_week_checks,
                                                            'month_checks':month_checks,
                                                            'two_month_checks':two_month_checks,
                                                            'more_months_checks':more_months_checks,
                                                            'total_to_pay_checks':total_to_pay_checks,
                                                            })

@login_required
def third_p_check_detail(request, year, month, day, third_p_check):

    third_p_check = get_object_or_404(ThirdPartyChecks, slug=third_p_check,
                                                            fecha_ingreso__year = year,
                                                            fecha_ingreso__month = month,
                                                            fecha_ingreso__day = day)                                                            

    '''
    if request.method == 'POST':

        change_state_form = ChangeStateForm(request.POST)

        if change_state_form.is_valid():
            third_p_check.change_state()

            return redirect(third_p_check.get_absolute_url())
    else:
        change_state_form = ChangeStateForm()
    '''

    if request.method == 'POST' and request.POST.get("delete_token"):
        parent = third_p_check.content_object
        parent_model = parent.__class__.__name__

        #acá va a ir el modelo de las ventas de granos también
        if parent_model == 'Sales':
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

    return render(request, 'funds/funds_self_checks.html',{
                                                            'self_checks':self_checks,
                                                            'today_checks':today_checks,
                                                            'week_checks':week_checks,
                                                            'two_week_checks':two_week_checks,
                                                            'month_checks':month_checks,
                                                            'two_month_checks':two_month_checks,
                                                            'more_months_checks':more_months_checks,
                                                            'total_to_pay_checks':total_to_pay_checks,
                                                                    })
@login_required
def self_check_detail(request, self_check):

    self_check = get_object_or_404(SelfChecks, slug=self_check)

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

    else:
        destroy_object_form = DestroyObjectForm()

    return render(request, 'funds/self_check_detail.html',{
                                                            'self_check':self_check,
                                                            'change_state_form':change_state_form,
                                                            'destroy_object_form':destroy_object_form,
                                                            })                                                            
