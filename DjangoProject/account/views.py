from django.shortcuts import render, HttpResponseRedirect, redirect
from .forms import RegistrationForm, UserProfileForm, LoginForm, UserForm, ChangepwdForm
from .models import UserProfile
from django.conf import settings
from django.http import HttpResponse
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from itsdangerous import URLSafeTimedSerializer as Utsr
import base64


# Create your views here.


class Token:
    def __init__(self, security_key):
        self.security_key = security_key
        self.salt = base64.encodestring(security_key.encode(encoding='utf-8'))

    def generate_validate_token(self, username):
        serializer = Utsr(self.security_key)
        return serializer.dumps(username, self.salt)

    def confirm_validate_token(self, token, expiration=3600):
        serializer = Utsr(self.security_key)
        return serializer.loads(token, salt=self.salt, max_age=expiration)

    def remove_validate_token(self, token):
        serializer = Utsr(self.security_key)
        print(serializer.loads(token, salt=self.salt))
        return serializer.loads(token, salt=self.salt)


token_confirm = Token(settings.SECRET_KEY)

# 登录


def user_login(request):
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            cd = login_form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user:
                login(request, user)
                return HttpResponseRedirect('/home')
            else:
                return HttpResponseRedirect('/account/login')
        else:
            return HttpResponse("登录失败")
    if request.method == "GET":
        login_form = LoginForm()
        return render(request, "account/login.html", {"form": login_form})

# 注册


def user_register(request):
    if request.method == "POST":
        user_form = RegistrationForm(request.POST)
        userprofile_form = UserProfileForm(request.POST)
        if user_form.is_valid()*userprofile_form.is_valid():
            username = user_form.cleaned_data['username']
            email = user_form.cleaned_data['email']

            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.is_active = False
            new_user.save()

            new_profile = userprofile_form.save(commit=False)
            new_profile.user = new_user
            new_profile.save()

            token = token_confirm.generate_validate_token(username)
            url = '/'.join(['http://39.108.219.254/account/activate', token])
            html_message = u'<h3>Hi!<br>' + username + \
                           '</h3><h4>欢迎加入</h4><h4>请访问该链接，完成用户验证:</h4><a href=\"' \
                           + url + '\">' \
                           + url + '</a>'
            msg = EmailMultiAlternatives(u'测试注册用户验证信息', html_message, "1903959864@qq.com", [email])
            msg.attach_alternative(html_message, "text/html")
            msg.send()

            return HttpResponse(u"请登录到注册邮箱中验证用户，有效期为1个小时。")
        else:
            return HttpResponse("此用户名已存在，请重新注册")
    else:
        return render(request, "account/register.html")

# 邮箱激活


def active_user(request, token):
    try:
        username = token_confirm.confirm_validate_token(token)
    except:
        username = token_confirm.remove_validate_token(token)
        users = User.objects.filter(username=username)
        for user in users:
            user.delete()
        return render(request, 'account/message.html',
                      {'message': u'对不起，验证链接已经过期，请重新<a href=\"' +
                                  u'/account/register\">注册</a>'})
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, 'account/message.html', {'message': u"对不起，您所验证的用户不存在，请重新注册"})
    user.is_active = True
    user.save()
    message = u'验证成功，请进行<a href=\"' + u'/account/login\">登录</a>操作'
    return render(request, 'account/message.html', {'message': message})
# 个人设置


@login_required(login_url="/account/login/")
def myself_info(request):
    userprofile = UserProfile.objects.get(user=request.user)
    if request.method == "POST":
        userprofile_form = UserForm(request.POST)
        if userprofile_form.is_valid():
            userprofile_cd = userprofile_form.cleaned_data
            userprofile.birth = userprofile_cd["birth"]
            userprofile.sex = userprofile_cd["sex"]
            userprofile.aboutme = userprofile_cd["aboutme"]
            userprofile.save()
        return HttpResponseRedirect('/account/myself_info')
    else:
        userprofile_form = UserForm(initial={"birth": userprofile.birth, "sex": userprofile.sex, "aboutme": userprofile.aboutme})
        return render(request, "account/myself_info.html", {"userprofile_form": userprofile_form})
# 图片设置


@login_required(login_url="/account/login/")
def myself_tou(request):
    return render(request, 'account/myself_tou.html')


@login_required(login_url="/account/login/")
def myself_mi(request):
    if request.method == 'GET':
        form = ChangepwdForm()
        return render(request, 'account/myself_mi.html', {'form': form})
    else:
        form = ChangepwdForm(request.POST)
        if form.is_valid():
            username = request.user.username
            oldpassword = request.POST.get('oldpassword', '')
            user = authenticate(username=username, password=oldpassword)
            if user is not None and user.is_active:
                newpassword = request.POST.get('newpassword1', '')
                user.set_password(newpassword)
                user.save()
                return redirect('/account/logout')
            else:
                return render(request, 'account/myself_mi.html', {'oldpassword_is_wrong': True})
        else:
            return render(request, 'account/myself_mi.html', {'form': form})
# 图片上传


def my_image(request):
    if request.method == "POST":
        img = request.POST['img']
        userprofile = UserProfile.objects.get(user=request.user)
        userprofile.photo = img
        userprofile.save()
        return HttpResponse("1")
    else:
        return render(request, "account/imagecrop.html",)
