import imp
from django.shortcuts import get_object_or_404, render, redirect
from expenses.models import Expenses
from payments.models import Payments, ThirdPartyChecks, SelfChecks
from payments.forms import ChangeStateForm
from purchases.models import Purchases
from sales.models import Sales
from .forms import FundManualMoveForm
from .models import FundManualMove
from sowing.models import SowingPurchases
from django.contrib.auth.decorators import login_required

@login_required
def funds_main(request):

    purchases = Purchases.objects.all()
    sales = Sales.objects.all()
    expenses = Expenses.objects.all()
    sowing_purchases = SowingPurchases.objects.all()


    purchase_cash_payed_totals = []
    purchase_trans_payed_totals = []
    for purchase in purchases:
        purchase_cash_payed_total = sum(list(map(int,purchase.payments.filter(tipo='efectivo').values_list('monto',flat=True))))
        purchase_trans_payed_total = sum(list(map(int,purchase.payments.filter(tipo='transferencia').values_list('monto',flat=True))))
        purchase_cash_payed_totals.append(purchase_cash_payed_total)
        purchase_trans_payed_totals.append(purchase_trans_payed_total)

    sale_cash_payed_totals = []
    sale_trans_payed_totals = []
    for sale in sales:
        sale_cash_payed_total = sum(list(map(int,sale.payments.filter(tipo='efectivo').values_list('monto',flat=True))))
        sale_trans_payed_total = sum(list(map(int,sale.payments.filter(tipo='transferencia').values_list('monto',flat=True))))
        sale_cash_payed_totals.append(sale_cash_payed_total)
        sale_trans_payed_totals.append(sale_trans_payed_total)

    expense_cash_payed_totals = []
    expense_trans_payed_totals = []
    for expense in expenses:
        expense_cash_payed_total = sum(list(map(int,expense.payments.filter(tipo='efectivo').values_list('monto',flat=True))))
        expense_trans_payed_total = sum(list(map(int,expense.payments.filter(tipo='transferencia').values_list('monto',flat=True))))
        expense_cash_payed_totals.append(expense_cash_payed_total)
        expense_trans_payed_totals.append(expense_trans_payed_total)

    sowing_purchase_cash_payed_totals = []
    sowing_purchase_trans_payed_totals = []
    for sowing_purchase in sowing_purchases:
        sowing_purchase_cash_payed_total = sum(list(map(int,sowing_purchase.payments.filter(tipo='efectivo').values_list('monto',flat=True))))
        sowing_purchase_trans_payed_total = sum(list(map(int,sowing_purchase.payments.filter(tipo='transferencia').values_list('monto',flat=True))))
        sowing_purchase_cash_payed_totals.append(sowing_purchase_cash_payed_total)
        sowing_purchase_trans_payed_totals.append(sowing_purchase_trans_payed_total)

    purchase_cash_total = sum(purchase_cash_payed_totals)
    sale_cash_total = sum(sale_cash_payed_totals)
    expense_cash_total = sum(expense_cash_payed_totals)
    sowing_purchases_cash_total = sum(sowing_purchase_cash_payed_totals)

    purchase_trans_total = sum(purchase_trans_payed_totals)
    sale_trans_total = sum(sale_trans_payed_totals)
    expense_trans_total = sum(expense_trans_payed_totals)
    sowing_purchases_trans_total = sum(sowing_purchase_trans_payed_totals)

    manualmoves_cash = FundManualMove.objects.filter(tipo='efectivo')
    manualmoves_cash_add_total = sum(list(map(int,manualmoves_cash.filter(action='agregar').values_list('monto',flat=True))))
    manualmoves_cash_remove_total = sum(list(map(int,manualmoves_cash.filter(action='quitar').values_list('monto',flat=True))))

    manualmoves_trans = FundManualMove.objects.filter(tipo='transferencia')
    manualmoves_trans_add_total = sum(list(map(int,manualmoves_trans.filter(action='agregar').values_list('monto',flat=True))))
    manualmoves_trans_remove_total = sum(list(map(int,manualmoves_trans.filter(action='quitar').values_list('monto',flat=True))))


    cash_total = sale_cash_total - expense_cash_total - purchase_cash_total + manualmoves_cash_add_total - manualmoves_cash_remove_total - sowing_purchases_cash_total

    trans_total = sale_trans_total - purchase_trans_total - expense_trans_total + manualmoves_trans_add_total - manualmoves_trans_remove_total - sowing_purchases_trans_total

    return render(request, 'funds/funds_main.html',{
                                                    'cash_total':cash_total,
                                                    'trans_total':trans_total,
                                                    })
                                                    
@login_required
def funds_list(request, type_id=''):

    if type_id !='':
        payments = Payments.objects.filter(tipo = str(type_id))

    else:
        payments = Payments.objects.all()

    total_payments = payments.count()

    total = sum(map(int,payments.values_list('monto', flat=True)))

    return render(request, 'funds/funds_list.html',{'payments':payments,
                                                    'type_id':type_id,
                                                    'total_payments':total_payments,
                                                    'total':total,
                                                    })
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

    return render(request, 'funds/self_check_detail.html',{
                                                            'self_check':self_check
                                                            
                                                            })                                                            
