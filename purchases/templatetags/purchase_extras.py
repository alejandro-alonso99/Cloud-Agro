from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

def currency(dollars):
    dollars = round(float(dollars), 2)
    return "$%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])

register.filter('currency', currency)

def percentage(number):
    number = str(number) + '%'
    return number

register.filter('percentage',percentage)

def usd_currency(number):
    number = 'USD ' + str(number)
    return number

register.filter('usd_currency',usd_currency)

@register.filter(name='spanishy')
def spanishy(arg):
    if arg == 'purchases':
        arg = 'Compra'
    
    if arg == 'sales':
        arg = 'Venta'
    
    if arg == 'expenses':
        arg = 'Gasto'

    return arg

@register.filter(name='loop_maker')
def loop_maker(arg):
    return range(arg)

@register.simple_tag
def get_index(list,arg):
    return list[int(arg)]

@register.simple_tag
def get_index_tuple(tuple):
    tuple = list(tuple)
    return [i[0] for i in tuple]

def divide(a, b):
    return a / b

register.filter('divide',divide)
