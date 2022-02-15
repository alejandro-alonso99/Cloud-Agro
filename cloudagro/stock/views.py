from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from itertools import chain
from purchases.models import Animal, Purchases
from sales.models import SaleRow, Sales
from stock.models import ManualMove
from .forms import ManualMoveForm
from sowing.models import Applications, SowingPurchases
from django.contrib.auth.decorators import login_required

@login_required
def stock_list(request):

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

    return render(request, 'stock/stock_list.html', {'animal_choices':ANIMAL_CHOICES,
                                                        'category_totals':category_totals,
                                                        'totals_len':totals_len,
                                                        'choices_names':choices_names,
                                                     })

@login_required
def manualmove_detail(request, year, month, day, manualmove):
    manualmove = get_object_or_404(ManualMove, slug=manualmove,
                                                date__year = year,
                                                date__month = month,
                                                date__day= day)       

    return render(request, 'stock/manualmove_detail.html',{'manualmove':manualmove

                                                            })                  

@login_required                                                            
def manualmove_create(request):
    if request.method == 'POST':
        move_form = ManualMoveForm(data=request.POST)
        
        if move_form.is_valid:
           move_form.save()

        return redirect('stock:stock_list')
    
    else:
        move_form = ManualMoveForm()

    last_3_manual_moves = ManualMove.objects.all()[:3]

    return render(request, 'stock/manualmove_create.html',{
                                                            'move_form': move_form,
                                                            'last_3_manual_moves':last_3_manual_moves,
                                                            }) 

@login_required
def manualmove_list(request):   
    manualmoves = ManualMove.objects.all()
    return render(request,'stock/manualmove_list.html',{'manualmoves':manualmoves

                                                            })   
                                                                                                      
@login_required
def products_stock_list(request):

    products_lt_dict = SowingPurchases.calculate_lt_by_type()

    applications_lt_dict = Applications.calculate_lt_by_type()

    product_choices = list(map(str,SowingPurchases.objects.values_list('producto',flat=True)))

    product_lt_kg = {}
    for product in product_choices:
        product = product.lower()
        product_lt_kg[product] = products_lt_dict[product] - applications_lt_dict[product]


    return render(request, 'stock/products_list.html',{ 'product_lt_kg':product_lt_kg })