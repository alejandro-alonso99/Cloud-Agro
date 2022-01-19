from django.shortcuts import redirect, render, get_object_or_404

from .models import Payments
from .forms import DestroyObjectForm


def payment_detail(request, year, month, day, payment):

    payment = get_object_or_404(Payments, slug=payment,
                                                date__year = year,
                                                date__month = month,
                                                date__day = day )
    
    if request.method == 'POST':
        purchase = payment.content_object
        destroy_object_form = DestroyObjectForm(request.POST)
        payment.delete()
        purchase.save()
        
        return redirect(purchase.get_absolute_url())
        
    else:
        destroy_object_form = DestroyObjectForm()


    return render(request,'payments/payment_detail.html',{
                                                        'payment':payment,
                                                        'destroy_object_form': destroy_object_form,
                                                            })
