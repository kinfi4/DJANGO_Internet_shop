from django import forms

from main.models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
             'first_name', 'last_name', 'phone', 'address', 'buying_type', 'order_date', 'comment'
        )

#
#
# class AuthUserForm(AuthenticationForm, ModelForm):
#     class Meta:
#         model = User
#         fields = ('Login', 'Password')
