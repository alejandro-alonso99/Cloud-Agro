# Cloud-Agro
## What does this WebApp do?
### AgroCloud is an accounting and stock-managing web app created for industrial agriculture. It includes a wide variety of features that make it possible for an agriculture business to keep track of yearly farming campaigns. 

## This project Includes:

## Create views:
### Create views include forms, formsets, and other functionalities. Once you create an object, you are redirected to the objects detail. In this case, this user just sold 20 cows.
![gif](create_sale.gif)

## Detail views:
### Detail views give you information about the given object, some detail views include the option to add payments to the purchase/expense/sale, etc.
![detail_view](detail_view.jpeg)

## List views:
### List views include all objects of a give type, you can also easily see unpayed purchases/sales/expenses, etc., as well as querying the objects by a date range or by the name of the costumer or provider.
![list_view](list_view.png)

## Payments:
## Certain objects allow you to register payments in their detail-views, payments in cash or bank transfer and cheques are all coded using generic foreign-keys so that the models can be related to multiple other models on demand.



