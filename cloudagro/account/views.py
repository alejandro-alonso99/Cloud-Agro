from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from account.forms import SelectCampaignForm
from payments.models import SelfChecks
from harvest.models import Harvest
from purchases.models import Purchases, Animal
from purchases.forms import SearchForm
from sales.models import Sales, SaleRow, GrainSales
from expenses.models import Expenses
from sowing.models import SowingPurchases
from funds.models import FundManualMove
from payments.models import ThirdPartyChecks
from stock.models import ManualMove
from sowing.models import SowingPurchases, Applications
import difflib
from land.models import Campaign

@login_required
def dashboard(request):

    search_form = SearchForm()

    query = None

    def calculate_funds():
        purchases = Purchases.objects.all()
        sales = Sales.objects.all()
        expenses = Expenses.objects.all()
        sowing_purchases = SowingPurchases.objects.all()
        grain_sales = GrainSales.objects.all()
        self_checks = SelfChecks.objects.all()
        third_p_checks = ThirdPartyChecks.objects.all()

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
        

        grain_sales_cash_payed = sum([sum(list(map(int,grain_sale.payments.filter(tipo='efectivo').values_list('monto',flat=True)))) for grain_sale in grain_sales])
        grain_sales_bank_payed = sum([sum(list(map(int,grain_sale.payments.filter(tipo='transferencia').values_list('monto',flat=True)))) for grain_sale in grain_sales])
        

        if self_checks:
            payed_self_checks = self_checks.filter(estado='pagado')
            self_checks_total = sum([int(check.monto) for check in payed_self_checks])
        else:
            self_checks_total = 0
        
        if third_p_checks:
            payed_third_p_checks = third_p_checks.filter(estado='depositado')
            third_p_checks_payed = sum([int(check.monto) for check in payed_third_p_checks])
        else:
            third_p_checks_payed = 0

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


        cash_total = sale_cash_total - expense_cash_total - purchase_cash_total + manualmoves_cash_add_total - manualmoves_cash_remove_total - sowing_purchases_cash_total + grain_sales_cash_payed

        print(manualmoves_cash_add_total)

        trans_total = sale_trans_total - purchase_trans_total - expense_trans_total + manualmoves_trans_add_total - manualmoves_trans_remove_total - sowing_purchases_trans_total + grain_sales_bank_payed - self_checks_total + third_p_checks_payed
       
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

        product_choices = list(dict.fromkeys(product_choices))

        product_choices = [x.lower() for x in product_choices]

        if 'query' in request.GET:
            form = SearchForm(request.GET)
            if form.is_valid():
                query = form.cleaned_data['query']
                product_choices = difflib.get_close_matches(query, product_choices)


        product_lt_kg = {}
        for product in product_choices:
            if product in applications_lt_dict.keys():
                product = product.lower()
                product_lt_kg[product] = products_lt_dict[product] - applications_lt_dict[product]
            else:
                product_lt_kg[product] = products_lt_dict[product]

        return product_lt_kg

    def calculate_cereal_stock():
        harvests = Harvest.objects.all()
        grain_sales = GrainSales.objects.all()

        cereal_dict = {}
        for harvest in harvests:
            lote = harvest.lote
            lote_type = lote.tipo
            
            if lote_type in cereal_dict:
                cereal_dict[lote_type] += harvest.kg_totales

            else:
                cereal_dict[lote_type] = harvest.kg_totales
        
        for sale in grain_sales:
            sale_type = sale.grano

            if sale_type in cereal_dict:
                cereal_dict[sale_type] -= sale.calculate_total_kg()

            else:
                cereal_dict[lote_type] = sale.calculate_total_kg()

        return cereal_dict


    cash_total = calculate_funds()[0]
    bank_total = calculate_funds()[1]
    third_p_checks_total = calculate_funds()[2]

    category_totals = calculate_animals_stock()[0]
    choices_names = calculate_animals_stock()[1]
    totals_len = calculate_animals_stock()[2]

    product_lt_kg = calculate_products_stock()

    cereal_dict = calculate_cereal_stock()

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            product_lt_kg = calculate_products_stock()
    
    return render(request, 'account/dashboard.html',{
                                                    'cash_total':cash_total,
                                                    'bank_total':bank_total,
                                                    'category_totals':category_totals,
                                                    'choices_names':choices_names,
                                                    'totals_len':totals_len,
                                                    'third_p_checks_total':third_p_checks_total,
                                                    'product_lt_kg':product_lt_kg,
                                                    'cereal_dict':cereal_dict,
                                                    'search_form':search_form,
                                                    'query':query,
                                                    })

def change_campaign(request):

    if 'campaign' in request.session:
        if request.session['campaign'] != []:
            campana = Campaign.objects.get(nombre=request.session['campaign']) 
        else:
            campana = []
    elif Campaign.objects.all():
        campana = Campaign.objects.all()[0]

    select_campaign_form = SelectCampaignForm(request.POST or None)

    if select_campaign_form.is_valid():

        campaign = select_campaign_form.cleaned_data.get('campaign')

        request.session['campaign'] = campaign
        
        return redirect('account:dashboard')

    return render(request,'account/change_campaign.html',{
                                                        'select_campaign_form':select_campaign_form,
                                                        'campana':campana,
                                                        })