from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404

from expenses.models import Expenses
from .forms import ExpenseForm

from payments.models import Payments
from payments.forms import PaymentForm

def expenses_list(request, category_id=''):

    if category_id != '':
        expenses = Expenses.objects.filter(categoria = str(category_id))
    
    else:
        expenses = Expenses.objects.all()

    total_expenses = expenses.count()
    unpayed_expenses = expenses.filter(status = 'por pagar')
    total_unpayed_expenses = unpayed_expenses.count()

    amount_to_pay_total = []
    for expense in unpayed_expenses:
        amount_to_pay = expense.calculate_amount_to_pay()
        amount_to_pay_total.append(amount_to_pay)
    
    amount_to_pay_total = sum(amount_to_pay_total)

    return render(request, 'expenses/expenses_list.html',{'expenses':expenses,
                                                            'category_id':category_id,
                                                            'total_expenses':total_expenses,
                                                            'total_unpayed_expenses':total_unpayed_expenses,
                                                            'amount_to_pay_total':amount_to_pay_total,
                                                            })

def expense_create(request):

    if request.method == 'POST':
        expense_form = ExpenseForm(data=request.POST)

        if expense_form.is_valid():
            expense_form.save()
        
        return redirect('expenses:expenses_list')
    
    else:
        expense_form = ExpenseForm()
    
    last_3_expenses = Expenses.objects.all()[:3]

    return render(request, 'expenses/expense_create.html',{
                                                            'expense_form': expense_form,
                                                            'last_3_expenses':last_3_expenses
                                                            }) 

def expenses_summary(request):

    CATEGORY_CHOICES = (
        ('costos directos', 'Costos Directos'),
        ('gastos de comercializacion', 'Gastos de Comercializacion'),
        ('gastos financieros', 'Gastos financieros'),
        ('costos de estructura', 'Costos de estructura'),
        ('impuestos', 'Impuestos'),
    )

    #Vector de montos totales por categoría de gasto.
    expense_category_totals = []
    expenses_by_category = []
    for choice in CATEGORY_CHOICES:
        expense_by_category = Expenses.objects.filter(categoria = str(choice[0]))
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
        expense_by_category = Expenses.objects.filter(categoria = category)
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
                                                                })

def expense_detail(request, year, month, day, expense):
    expense = get_object_or_404(Expenses, slug=expense,
                                                date__year = year,
                                                date__month = month,
                                                date__day = day )

    #PAGOS
    payments = expense.payments


    total_payed = sum(list(map(int,payments.values_list('monto', flat=True))))

    if expense.monto - total_payed <=0:
        expense.change_status('pagado')
        expense.save()


    initial_payment_data = {
        'content_type': expense.get_content_type,
        'object_id': expense.id,
    }

    payment_form = PaymentForm(request.POST or None, initial= initial_payment_data)

    if payment_form.is_valid():
        content_type = payment_form.cleaned_data.get('content_type')
        obj_id = payment_form.cleaned_data.get('object_id')
        monto = payment_form.cleaned_data.get('monto')
        tipo = payment_form.cleaned_data.get('tipo')

        attrs = {'content_type':content_type, 'object_id':obj_id, 'monto':monto, 'tipo':tipo}

        new_payment = Payments(**attrs)
        new_payment.save() 
        return redirect(expense.get_absolute_url())          

    return render(request, 'expenses/expense_detail.html',{'expense':expense,
                                                            'payment_form':payment_form,
                                                            'payments':payments,
                                                                })                                            