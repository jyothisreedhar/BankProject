from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, LoginForm, AccountCreateForm, TransactionCreateForm
from django.views.generic import TemplateView
from .models import CustomUser, Account, Transactions
from django.contrib.auth import authenticate, login as djangologin
from django.utils.decorators import method_decorator
from .decorators import account_validator


class Registration(TemplateView):
    model = CustomUser
    form_class = UserRegistrationForm
    template_name = "registration.html"
    context = {}

    def get(self, request, *args, **kwargs):
        # form=self.form_class()
        self.context["form"] = self.form_class()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "login.html")
        else:
            self.context["form"] = form
            return render(request, self.template_name, self.context)


class LoginView(TemplateView):
    model = CustomUser
    template_name = "login.html"
    form_class = LoginForm
    context = {}

    def get(self, request, *args, **kwargs):
        self.context["form"] = self.form_class()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")  # lakshmi
            password = form.cleaned_data.get("password")  # lakshmi@123
            print(username, password)
            # user=authenticate(request,username=username,password=password)
            user = self.model.objects.get(username=username)

            if (user.username == username) & (user.password == password):
                djangologin(request, user)
                print("success")
                return redirect("index")
                # check for logined user accout sts

                # try:
                #     account = Account.objects.get(user=request.user)
                #     status = account.active_status
                #     # print(status)
                #     flag = True if status == "active" else False
                #     # print(flag)
                #     self.context["flag"] = flag
                #     return render(request, "home.html", self.context)
                #
                # except:
                #     return render(request, "home.html", self.context)
            else:

                print("fail")
                return render(request, self.template_name, self.context)


def index(request):
    context = {}
    try:
        account = Account.objects.get(user=request.user)
        status = account.active_status
        # print(status)
        flag = True if status == "active" else False
        # print(flag)
        context["flag"] = flag
        return render(request, "home.html", context)

    except:
        return render(request, "home.html", context)


@method_decorator(account_validator, name='dispatch')
class AccountCreateView(TemplateView):
    model = Account
    template_name = "createaccount.html"
    form_class = AccountCreateForm
    context = {}

    def get(self, request, *args, **kwargs):
        account_number = ""

        # account numbr auyomatically increased when new user register
        account = self.model.objects.all().last()
        if account:
            acno = int(account.account_number.split("-")[1]) + 1  # "sbk-1000"
            print("SBK-", acno)
            account_number = "SBK-" + str(acno)

        else:
            account_number = "SBK-1000"
        self.context["form"] = self.form_class(initial={"account_number": account_number, "user": request.user})

        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect("index")
        else:
            self.context["form"] = form
            return render(request, self.template_name, self.context)


class GetUserMixin(object):
    def get_user(self, account_num):
        return Account.objects.get(account_number=account_num)


class TransactionsView(TemplateView, GetUserMixin):
    model = Transactions
    template_name = "transactions.html"
    form_class = TransactionCreateForm
    context = {}

    def get(self, request, *args, **kwargs):
        self.context["form"] = self.form_class(initial={"user": request.user})
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # pass
            to_account = form.cleaned_data.get("to_account_number")  # lakshmi
            amount = form.cleaned_data.get("amount")
            remarks = form.cleaned_data.get("remarks")
            account = self.get_user(to_account)
            account.balance += int(amount)
            account.save()
            cur_acct = Account.objects.get(user=request.user)
            cur_acct.balance -= int(amount)
            cur_acct.save()
            transaction = Transactions(user=request.user,
                                       amount=amount,
                                       to_accno=to_account,
                                       remarks=remarks)

            transaction.save()
            return redirect("index")
        else:
            self.context["form"] = form
            return render(request, self.template_name,self.context)


class BalanceEnq(TemplateView):
    def get(self, request, *args, **kwargs):
        account = Account.objects.get(user=request.user)
        balance = account.balance
        return JsonResponse({"balance":balance})
        #return render(request, "balancecheck.html", {"balance": balance})


#
class TransactionHistory(TemplateView):
    def get(self, request, *args, **kwargs):
        debit_transactions = Transactions.objects.filter(user=request.user)

        # fetch accno of logined user
        login_user = Account.objects.get(user=request.user)
        credit_transactions = Transactions.objects.filter(to_accno=login_user.account_number)
        return render(request, "transactionhistory.html", {"debit_transactions": debit_transactions,
                                                           "credit_transactions": credit_transactions})
