from django.shortcuts import get_object_or_404, render, redirect
from payments.models import ThirdPartyChecks, SelfChecks
from payments.forms import ChangeStateForm
from .forms import FundManualMoveForm
from .models import FundManualMove
from django.contrib.auth.decorators import login_required

@login_required
def fund_manualmove_create(request):

    if request.method == 'POST':
        move_form = FundManualMoveForm(data=request.POST)
        
        if move_form.is_valid:
           move_form.save()

        return redirect('funds:funds_main')
    
    else:
        move_form = FundManualMoveForm()

    last_3_manual_moves = FundManualMove.objects.all()[:3]

    return render(request, 'funds/funds_manualmove_create.html',{
                                                            'move_form': move_form,
                                                            'last_3_manual_moves':last_3_manual_moves,
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


    if request.method == 'POST':

        change_state_form = ChangeStateForm(request.POST)

        if change_state_form.is_valid():
            third_p_check.change_state()

            return redirect(third_p_check.get_absolute_url())
    else:
        change_state_form = ChangeStateForm()

    return render(request, 'funds/third_p_check_detail.html',{
                                                        'third_p_check' : third_p_check,
                                                        'change_state_form':change_state_form,
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

    if request.method == 'POST':

        change_state_form = ChangeStateForm(request.POST)

        if change_state_form.is_valid():
            self_check.change_state()

            return redirect('funds:checks_self')

    else:
        change_state_form = ChangeStateForm()

    return render(request, 'funds/self_check_detail.html',{
                                                            'self_check':self_check,
                                                            'change_state_form':change_state_form,
                                                            })                                                            
