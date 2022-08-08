from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from harvest.models import GrainManualMove
from .forms import GrainMamualmoveForm
from purchases.forms import DateForm

@login_required
def grains_manualmove_create(request):

    if request.method == 'POST':
        move_form = GrainMamualmoveForm(data=request.POST)
        
        if move_form.is_valid:
           move_form.save()

        return redirect('account:dashboard')
    
    else:
        move_form = GrainMamualmoveForm()

    return render(request, "harvest/grains_manualmove_create.html",{'move_form':move_form})


@login_required
def grains_manualmove_list(request):   

    manualmoves = GrainManualMove.objects.all()

    date_form = DateForm()

    date_query_start = None
    date_query_end = None

    if 'date_query_start' and 'date_query_end' in request.GET:
        form = DateForm(request.GET)
        if form.is_valid():
            date_query_start = form.cleaned_data['date_query_start'].strftime("%Y-%m-%d")
            date_query_end = form.cleaned_data['date_query_end'].strftime("%Y-%m-%d")
            manualmoves = GrainManualMove.objects.filter(date__range=[date_query_start, date_query_end])

    return render(request,'harvest/grains_manualmove_list.html',{'manualmoves':manualmoves,
                                                        'date_form':date_form,
                                                        'date_query_start':date_query_start,
                                                        'date_query_end':date_query_end,
                                                        })   