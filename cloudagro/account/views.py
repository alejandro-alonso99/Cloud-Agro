from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from purchases.models import Purchases, Animal
from sales.models import Sales, SaleRow
from expenses.models import Expenses
from sowing.models import SowingPurchases
from funds.models import FundManualMove
from payments.models import ThirdPartyChecks
from stock.models import ManualMove
from sowing.models import SowingPurchases, Applications

@login_required
def dashboard(request):

    def calculate_funds():
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

        third_p_checks = ThirdPartyChecks.objects.all()

        to_deposit_checks = third_p_checks.filter(estado= 'a depositar')

        third_p_checks_total = sum(list(map(int,to_deposit_checks.values_list('monto',flat=True)))) 

        return cash_total, trans_total, third_p_checks_total

    def calculate_animals_stock():

        ANIMAL_CHOICES = (
        ('ternero','Ternero'),
        ('ternera','Ternera'),
        ('novillo','Novillo'),
        ('vaquillona','Vaquillona'),
        ('vaca','Vaca')
        
        )

        #Vector de compras de animales totales por categoría
        purchase_category_totals=[]
        for item in ANIMAL_CHOICES:
            purchase_category_animals = Animal.objects.filter(categoria = str(item[0]))
            purchase_category_total = sum(list(map(int,purchase_category_animals.values_list('cantidad', flat=True))))
            purchase_category_totals.append(purchase_category_total)

        #Vector de ventas de animales totales por categoría
        sale_category_totals=[]
        for item in ANIMAL_CHOICES:
            sale_category_animals = SaleRow.objects.filter(categoria = str(item[0]))
            sale_category_total = sum(list(map(int,sale_category_animals.values_list('cantidad', flat=True))))
            sale_category_totals.append(sale_category_total)

        #Vector de animales totales por categoría agregados a mano
        manual_add_category_totals=[]
        for item in ANIMAL_CHOICES:
            manual_add_category = ManualMove.objects.filter(tipo='agregado',categoria= str(item[0]))
            manual_add_category_total = sum(list(map(int,manual_add_category.values_list('cantidad', flat=True))))
            manual_add_category_totals.append(manual_add_category_total)

        #Vector de animales totales por categoría quitados a mano
        manual_remove_category_totals=[]
        for item in ANIMAL_CHOICES:
            manual_remove_category = ManualMove.objects.filter(tipo='quitado',categoria= str(item[0]))
            manual_remove_category_total = sum(list(map(int,manual_remove_category.values_list('cantidad', flat=True))))
            manual_remove_category_totals.append(manual_remove_category_total)

        #Vector total
        category_totals = [a-b+c-d for a,b,c,d in zip(purchase_category_totals,sale_category_totals,manual_add_category_totals,manual_remove_category_totals)]

        #Vector de nombres
        choices_names = [i[1] for i in list(ANIMAL_CHOICES)]
        
        totals_len = len(purchase_category_totals)

        return category_totals, choices_names, totals_len

    def calculate_products_stock():

        products_lt_dict = SowingPurchases.calculate_lt_by_type()

        applications_lt_dict = Applications.calculate_lt_by_type()

        product_choices = list(map(str,SowingPurchases.objects.values_list('producto',flat=True)))

        product_lt_kg = {}
        for product in product_choices:
            product = product.lower()
            product_lt_kg[product] = products_lt_dict[product] - applications_lt_dict[product]
        
        return product_lt_kg

    cash_total = calculate_funds()[0]
    bank_total = calculate_funds()[1]
    third_p_checks_total = calculate_funds()[2]

    category_totals = calculate_animals_stock()[0]
    choices_names = calculate_animals_stock()[1]
    totals_len = calculate_animals_stock()[2]

    product_lt_kg = calculate_products_stock()

    return render(request, 'account/dashboard.html',{
                                                    'cash_total':cash_total,
                                                    'bank_total':bank_total,
                                                    'category_totals':category_totals,
                                                    'choices_names':choices_names,
                                                    'totals_len':totals_len,
                                                    'third_p_checks_total':third_p_checks_total,
                                                    'product_lt_kg':product_lt_kg,
                                                    })