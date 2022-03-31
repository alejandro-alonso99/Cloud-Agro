from django.shortcuts import get_object_or_404, redirect, render
from purchases.models import Animal
from sales.models import SaleRow
from stock.models import ManualMove
from .forms import ManualMoveForm
from sowing.models import Applications, SowingPurchases
from django.contrib.auth.decorators import login_required
from payments.forms import DestroyObjectForm

@login_required
def manualmove_detail(request, year, month, day, manualmove):
    manualmove = get_object_or_404(ManualMove, slug=manualmove,
                                                date__year = year,
                                                date__month = month,
                                                date__day= day)       

    if request.method == 'POST':
        destroy_object_form = DestroyObjectForm(request.POST)
        manualmove.delete()

        return redirect('stock:manualmove_list')

    else:
        destroy_object_form = DestroyObjectForm()

    return render(request, 'stock/manualmove_detail.html',{'manualmove':manualmove,
                                                            'destroy_object_form':destroy_object_form
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