from django.forms import ModelForm
from .models import CustomUser, Account, Transactions
from django import forms


class UserRegistrationForm(ModelForm):
    #password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password", "age", "phone"]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'username'}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'email'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'password'}),
            'age': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'age'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'phone'}),
        }



class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


class AccountCreateForm(ModelForm):
    class Meta:
        model = Account
        fields = ["account_number", "balance", "ac_type", "user", "active_status"]


class TransactionCreateForm(forms.Form):
    user = forms.CharField()
    to_account_number = forms.CharField(widget=forms.PasswordInput)
    confirm_account_number = forms.CharField()
    amount = forms.CharField(max_length=5)
    remarks = forms.CharField()

    def clean(self):
        cleaned_data = super().clean()
        to_account_number = cleaned_data.get("to_account_number")
        confirm_account_number = cleaned_data.get("confirm_account_number")
        amount = int(cleaned_data.get("amount"))
        user = cleaned_data.get("user")
        print(to_account_number, confirm_account_number)

        # check the given account number valid or not
        try:
            account = Account.objects.filter(account_number=to_account_number)
        # if not account:
        except:
            msg = "Invalid Account Number"
            self.add_error('to_account_number', msg)

        # check from and to account number match
        if to_account_number != confirm_account_number:
            msg = "Account Number Mismatch"
            self.add_error('to_account_number', msg)

        # check balance
        account = Account.objects.get(user__username=user)
        aval_bal = account.balance
        if amount > aval_bal:
            message = "Insufficient Balance"
            self.add_error("amount", message)





# username:jyothi
# pswd:jyothi@123
