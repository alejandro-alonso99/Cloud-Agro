from django.shortcuts import redirect, render, get_object_or_404
from .models import Payments
from .forms import DestroyObjectForm
from django.contrib.auth.decorators import login_required

@login_required
def payment_detail(request, year, month, day, payment):

    payment = get_object_or_404(Payments, slug=payment,
                                                date__year = year,
                                                date__month = month,
                                                date__day = day )
    
    if request.method == 'POST':
        parent = payment.content_object
        parent_model = parent.__class__.__name__
        if parent_model == 'Purchases' or parent_model == 'SowingPurchases' or parent_model == 'Expenses':
            parent.status = 'por pagar'
            parent.save()

        elif parent_model == 'Sales':
            parent.status = 'por cobrar'
            parent.save()


        destroy_object_form = DestroyObjectForm(request.POST)
        payment.delete()
        
        return redirect(parent.get_absolute_url())
        
    else:
        destroy_object_form = DestroyObjectForm()


    return render(request,'payments/payment_detail.html',{
                                                        'payment':payment,
                                                        'destroy_object_form': destroy_object_form,
                                                            })
