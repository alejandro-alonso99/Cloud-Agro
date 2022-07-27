from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from expenses.models import Expenses
from .forms import ExpenseForm, FilterExpenseForm
from payments.models import Payments, SelfChecks, ThirdPartyChecks, EndorsedChecks
from payments.forms import PaymentForm, SelfChecksForm, EndorsedChecksForm, DestroyObjectForm
from purchases.forms import DateForm
from land.models import Campaign

@login_required
def expenses_list(request, category_id=''):

    if 'campaign' in request.session:
        campana = Campaign.objects.get(nombre=request.session['campaign']) 
    elif Campaign.objects.all():
        campana = Campaign.objects.all()[0]

    date_form = DateForm()

    filter_expense = FilterExpenseForm()

    date_query_start = None
    date_query_end = None

    filter_query = None

    expenses = Expenses.objects.filter(campana=campana)

    total_expenses = expenses.count()
    unpayed_expenses = expenses.filter(status = 'por pagar')
    total_unpayed_expenses = unpayed_expenses.count()

    amount_to_pay_total = []
    for expense in unpayed_expenses:
        amount_to_pay = expense.calculate_amount_to_pay()
        amount_to_pay_total.append(amount_to_pay)
    
    amount_to_pay_total = sum(amount_to_pay_total)


    if 'date_query_start' and 'date_query_end' in request.GET:
        form = DateForm(request.GET)
        if form.is_valid():
            date_query_start = form.cleaned_data['date_query_start'].strftime("%Y-%m-%d")
            date_query_end = form.cleaned_data['date_query_end'].strftime("%Y-%m-%d")
            expenses = expenses.filter(date__range=[date_query_start, date_query_end])

    if 'filter_query' in  request.GET:
        form = FilterExpenseForm(request.GET)
        if form.is_valid():
            filter_query = form.cleaned_data['filter_query']
            expenses = expenses.filter(categoria = filter_query)




    return render(request, 'expenses/expenses_list.html',{'expenses':expenses,
                                                            'category_id':category_id,
                                                            'total_expenses':total_expenses,
                                                            'total_unpayed_expenses':total_unpayed_expenses,
                                                            'amount_to_pay_total':amount_to_pay_total,
                                                            'date_form':date_form,
                                                            'date_query_start':date_query_start,
                                                            'date_query_end':date_query_end,
                                                            'filter_expense':filter_expense,
                                                            'filter_query':filter_query
                                                            })
@login_required
def expense_create(request):

    if 'campaign' in request.session:
        campana = Campaign.objects.get(nombre=request.session['campaign']) 
    elif Campaign.objects.all():
        campana = Campaign.objects.all()[0]

    if request.method == 'POST':
        expense_form = ExpenseForm(data=request.POST)

        if expense_form.is_valid():
            new_expense = expense_form.save(commit=False)
            new_expense.campana = campana
            new_expense.save()
        
        return redirect('expenses:expenses_list')
    
    else:
        expense_form = ExpenseForm()
    
    return render(request, 'expenses/expense_create.html',{
                                                            'expense_form': expense_form,
                                                            }) 
@login_required
def expenses_summary(request):

    CATEGORY_CHOICES = (
        ('costos directos', 'Costos Directos'),
        ('gastos de comercializacion', 'Gastos de Comercializacion'),
        ('gastos financieros', 'Gastos financieros'),
        ('costos de estructura', 'Costos de estructura'),
        ('impuestos', 'Impuestos'),
    )

    if 'campaign' in request.session:
        campana = Campaign.objects.get(nombre=request.session['campaign']) 
    elif Campaign.objects.all():
        campana = Campaign.objects.all()[0]

    expenses = Expenses.objects.filter(campana=campana)

    #Vector de montos totales por categoría de gasto.
    expense_category_totals = []
    expenses_by_category = []
    for choice in CATEGORY_CHOICES:
        expense_by_category = expenses.filter(categoria = str(choice[0]))
        expenses_by_category_totals = sum(list(map(int,expense_by_category.values_list('monto', flat=True)))) 
        expense_category_totals.append(expenses_by_category_totals)
        expenses_by_category.append(expense_by_category)

    category_names = [i[0] for i in list(CATEGORY_CHOICES)]

    expenses_names_and_totals = zip(category_names, expense_category_totals)

    totals_len = len(expense_category_totals)

    expenses_dict = {}
    description_totals = []
    expense_category_descriptions = []

    #Diccionario con categoría: descripción: total por descripción
    for category in category_names:
        expenses_dict[category] = {}
        expense_by_category = expenses.filter(categoria = category)
        expense_category_descriptions = list(map(str,expense_by_category.values_list('descripcion', flat=True)))
        expense_category_descriptions = dict.fromkeys(expense_category_descriptions)
        for description in expense_category_descriptions:
            expense_by_category_and_desc = expense_by_category.filter(descripcion=description)
            description_total = sum(list(map(int,expense_by_category_and_desc.values_list('monto', flat=True))))    
            description_totals.append(description_total)
            expenses_dict[category][description] = description_total

    return render(request, 'expenses/expenses_summary.html',{'expenses_names_and_totals':expenses_names_and_totals,
                                                                'totals_len':totals_len,
                                                                'description_totals':description_totals,
                                                                'expenses_dict':expenses_dict,
                                                                'expense_category_descriptions':expense_category_descriptions,
                                                                'category_names':category_names,
                                                                'expense_category_totals':expense_category_totals,
                                                                })
@login_required
def expense_detail(request, id):
    expense = get_object_or_404(Expenses, id=id)

    #PAGOS
    payments = expense.payments

    self_checks = expense.self_checks

    self_checks = [check for check in self_checks if check.estado != 'anulado']
    
    third_p_checks = ThirdPartyChecks.objects.filter(estado='a depositar')

    endorsed_checks = expense.endorsed_checks


    if expense.calculate_amount_to_pay() <= 0:
        expense.status = 'pagado'
        expense.save()


    initial_payment_data = {
        'content_type': expense.get_content_type,
        'object_id': expense.id,
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
        return redirect(expense.get_absolute_url())          

    if self_check_form.is_valid():
        content_type = self_check_form.cleaned_data.get('content_type')
        obj_id = self_check_form.cleaned_data.get('object_id')
        fecha_pago = self_check_form.cleaned_data.get('fecha_pago')
        banco_emision = self_check_form.cleaned_data.get('banco_emision')
        numero_cheque = self_check_form.cleaned_data.get('numero_cheque')
        titular_cheque = self_check_form.cleaned_data.get('titular_cheque')
        monto = self_check_form.cleaned_data.get('monto')
        cliente = expense.concepto
        
        descripcion = expense.descripcion

        attrs = {'content_type':content_type, 'object_id':obj_id, 
                                                'cliente':cliente,
                                                'descripcion':descripcion,
                                                'fecha_pago':fecha_pago, 
                                                'banco_emision':banco_emision,
                                                'numero_cheque':numero_cheque,
                                                'titular_cheque':titular_cheque,
                                                'monto':monto}
        
        new_self_check = SelfChecks(**attrs)
        new_self_check.save()

        return redirect(expense.get_absolute_url())

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

        return redirect(expense.get_absolute_url())

    money_zip = zip(payments,self_checks)

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

            expense.delete()
            return redirect('expenses:expenses_list')
    else:
        destroy_object_form = DestroyObjectForm()

    return render(request, 'expenses/expense_detail.html',{'expense':expense,
                                                            'payment_form':payment_form,
                                                            'self_check_form':self_check_form,
                                                            'endorsed_checks_form':endorsed_checks_form,
                                                            'payments':payments,
                                                            'self_checks':self_checks,
                                                            'third_p_checks':third_p_checks,
                                                            'endorsed_checks':endorsed_checks,
                                                            'money_zip':money_zip,
                                                            'destroy_object_form':destroy_object_form,
                                                                })

@login_required
def expense_update(request, id):

    expense = get_object_or_404(Expenses, id=id)

    if request.method == 'POST':
        expense_form = ExpenseForm(data=request.POST)

        if expense_form.is_valid():

            payments = expense.payments

            self_checks = expense.self_checks

            endorsed_checks = expense.endorsed_checks

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

            concepto = expense_form.cleaned_data.get('concepto')
            monto = expense_form.cleaned_data.get('monto')
            descripcion = expense_form.cleaned_data.get('descripcion')
            categoria = expense_form.cleaned_data.get('categoria')
            campana = expense.campana
            date = expense.date

            attrs = {'concepto':concepto,
                    'monto':monto, 'descripcion':descripcion,
                    'categoria':categoria, 'date':date,
                    'status':'por pagar','campana':campana}
            
            expense = Expenses(id=id, **attrs)
            expense.save()
            
            return redirect(expense.get_absolute_url())
    
    else:
        expense_form = ExpenseForm()

    return render(request, 'expenses/expense_update.html',{
                                                            'expense_form':expense_form,
                                                            })