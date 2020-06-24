from django import forms


PAYMENT_CHOICES = (
    ('UPI', 'UPI'),
    ('COD', 'Cash on delievery ')
)


class CheckoutForm(forms.Form):
    room_no = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter Room No.',
        'class': 'form-control'
    }), required=True)
    wing_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter Wing Name',
        'class': 'form-control'
    }), required=True)
    save_info = forms.BooleanField(
        widget=forms.CheckboxInput(), required=False)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class PaymentForm(forms.Form):
    payment_sender_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Please enter sender name.',
        'class': 'form-control'
    }), required=True)


class RefundForm(forms.Form):
    order_id = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()
