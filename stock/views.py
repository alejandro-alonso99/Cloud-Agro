from django.shortcuts import get_object_or_404, redirect, render
from stock.models import ManualMove
from .forms import ManualMoveForm
from django.contrib.auth.decorators import login_required
from payments.forms import DestroyObjectForm
from purchases.forms import SearchForm, DateForm

@login_required
def manualmove_detail(request, id):
    manualmove = get_object_or_404(ManualMove, id=id)       

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
def manualmove_update(request, id):   

    manualmove = get_object_or_404(ManualMove, id=id)

    if request.method == 'POST':
        move_form = ManualMoveForm(data=request.POST)
        if move_form.is_valid():            
            campo = move_form.cleaned_data.get('campo')
            categoria = move_form.cleaned_data.get('categoria')
            cantidad = move_form.cleaned_data.get('cantidad')
            tipo = move_form.cleaned_data.get('tipo')

            date = manualmove.date

            args = {'campo':campo, 'categoria':categoria,
                    'cantidad':cantidad, 'tipo':tipo,
                    'date':date}
            
            manualmove = ManualMove(id=id, **args)
            manualmove.save()

            return redirect(manualmove.get_absolute_url())
    else:
        move_form = ManualMoveForm()

    return render(request, 'stock/manualmove_update.html',{
                                                            'manualmove':manualmove,
                                                            'move_form':move_form,
                                                            })

@login_required                                                            
def manualmove_create(request):
    if request.method == 'POST':
        move_form = ManualMoveForm(data=request.POST)
        
        if move_form.is_valid:
           move_form.save()

        return redirect('account:dashboard')
    
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

    date_form = DateForm()

    date_query_start = None
    date_query_end = None

    if 'date_query_start' and 'date_query_end' in request.GET:
        form = DateForm(request.GET)
        if form.is_valid():
            date_query_start = form.cleaned_data['date_query_start'].strftime("%Y-%m-%d")
            date_query_end = form.cleaned_data['date_query_end'].strftime("%Y-%m-%d")
            manualmoves = ManualMove.objects.filter(date__range=[date_query_start, date_query_end])

    return render(request,'stock/manualmove_list.html',{'manualmoves':manualmoves,
                                                        'date_form':date_form,
                                                        'date_query_start':date_query_start,
                                                        'date_query_end':date_query_end,
                                                        })   