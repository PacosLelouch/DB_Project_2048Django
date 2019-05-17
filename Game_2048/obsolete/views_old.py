from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from .game_program.game import Game
from .forms import *

# Create your views here.

dir_dict = {
    'up':1,
    'down':2,
    'left':3,
    'right':4,
}

this_game = None

def get_ip_addr(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip is None:
        ip = request.META['REMOTE_ADDR']
    return ip

def index(request):
    print(get_ip_addr(request), 'visits index.') #TEST
    context = {'valid':True}
    print('username:', request.session.get('username')) #TEST
    print('is login:', request.session.get('is_login')) #TEST
    if request.session.get('is_login'):
        context['is_login'] = True
        username = request.session.get('username')
        if username is None:
            return Http404('Invalid user.')
        context['username'] = username
    else:
        context['is_login'] = False
        if request.method == "POST":
            user = request.POST.get('username')
            pwd = request.POST.get('password')
            if len(user) <= 20 and len(pwd) <= 30 and user == "test" and pwd == "123": # TODO:在数据库中查询无重复
                if request.POST.get('box') == "1":   #checkbox被按下
                    request.session.set_expiry(10)  #session认证时间为10s，10s之后session认证失效
                request.session['username'] = user   #user的值发送给session里的username
                request.session['is_login'] = True   #认证为真
                return redirect('/Game_2048/check_login/')
            else:
                context['valid'] = False
    return render(request, 'Game_2048/index.html', context)

def check_login(request):
    print(get_ip_addr(request), 'visits check login.') #TEST
    print('check login:', request.session.get('is_login')) #TEST
    if request.session.get('is_login',None):  #若session认证为真
        # TODO:INSERT LOGIN_RECORD VALUES(...)
        return redirect('/Game_2048/')
    else:
        raise Http404('Invalid visit.')

def logout(request):
    print(get_ip_addr(request), 'visits logout.') #TEST
    if request.session.get('username') is not None:
        del request.session['username']
    if request.session.get('is_login') is not None:
        del request.session['is_login']
    print('check logout:', request.session.get('is_login')) #TEST
    return redirect('/Game_2048/')

def personal(request):
    print(get_ip_addr(request), 'visits personal.') #TEST
    user = request.session.get('username')
    is_login = request.session.get('is_login')
    context = {}
    if user is None or is_login != True:
        raise Http404('Invalid visit.')
    else:
        context['name'] = user
        #TODO: SELECT...
        return render(request, 'Game_2048/personal.html', context)

def message_board(request):
    print(get_ip_addr(request), 'visits messsage board.') #TEST
    user = request.session.get('username', None)
    is_login = request.session.get('is_login', None)
    context = {}
    if user is None or is_login != True:
        context['name'] = None
        context['guest'] = True
    else:
        context['name'] = user
        context['guest'] = False
    context['postmsg'] = ''
    if request.method == 'GET':
        #TODO
        pass
    elif request.method == 'POST':
        # TODO: INSERT MsgRecord VALUES(...)
        content = request.POST.get('content')
        if content is not None:
            context['postmsg'] = request.POST.get('content')
        #TODO
    else:
        raise Http404('Invalid visit')
    return render(request, 'Game_2048/message_board.html', context)

def register(request):
    print(get_ip_addr(request), 'visits register.') #TEST
    context = {'valid_register':True}
    if request.method == 'GET':
        return render(request, 'Game_2048/register.html', context)
    elif request.method == 'POST':
        user = request.POST.get('username')
        pwd = request.POST.get('password')
        email = request.POST.get('email')
        if len(user) <= 20 and len(pwd) <= 30 and len(email) <= 60 and user == "test": # TODO:在数据库中查询无重复
            # TODO:INSERT USER VALUES(...)
            request.session['reg_username'] = user
            request.session['reg_email'] = email
            return redirect('/Game_2048/check_register/')
        else:
            context['valid_register'] = False
    return render(request, 'Game_2048/register.html', context)

def check_register(request):
    print(get_ip_addr(request), 'visits check register.') #TEST
    print('check login:', request.session.get('valid_register')) #TEST
    name = request.session.get('reg_username')
    email = request.session.get('reg_email')
    if name is not None and email is not None:
        context = {'name':name, 'email':email}
        if request.session.get('reg_username') is not None:
            del request.session['reg_username']
        if request.session.get('reg_email') is not None:
            del request.session['reg_email']
        return render(request,'Game_2048/check_register.html', context)
    else:
        raise Http404('Invalid visit.')

def playing(request):  #问题: 游戏可以通过返回键退回操作，所以可能用js写游戏好些？
    global this_game
    print(get_ip_addr(request), 'visits playing.') #TEST
    name = request.session.get('username')
    is_login = request.session.get('is_login')
    #if this_game is None:
        #print(id(this_game), this_game) #TEST
    if name is None or is_login != True:
        raise Http404('Invalid user "' + str(name) + '".')
    direction = 'None'
    print('playing, request method:', request.method) #TEST
    if request.is_ajax(): #new experiment
        print("ajax request:", request.POST) #TEST
        if this_game is None:
            raise Http404('Invalid submission.')
        form = DirectionForm(request.POST)
        #print("form:", form) #TEST
        if not form.is_valid():
            raise Http404('Invalid visit.')
        direction = form.cleaned_data['direction']
        size = form.cleaned_data['size']
        if this_game.state == 1:
            this_game.move(dir_dict[direction])
        if not this_game.board.is_continue():
            this_game.over()
        print('after ajax:', this_game.to_json_with_last_move(direction)) #TEST
        response = HttpResponse(this_game.to_json_with_last_move(direction), content_type='application/json')
        print('res:', response) #TEST
        return response
    if request.method == 'POST':
        if this_game is None:
            raise Http404('Invalid submission.')
        form = DirectionForm(request.POST)
        if form.is_valid():
            direction = form.cleaned_data['direction']
            size = form.cleaned_data['size']
            if this_game.state == 1:
                this_game.move(dir_dict[direction])
            if not this_game.board.is_continue():
                this_game.over()
        else:
            raise Http404('Invalid visit.')
            #this_game = Game(name=name, size=size)
    elif request.method == 'GET':
        size = request.GET.get('size')
        print('size:', size) #TEST
        if size is None:
            raise Http404('Invalid size.')
        try:
            size = int(size)
        except:
            raise Http404('Invalid size.')
        this_game = Game(name=name, size=size)
        form = DirectionForm()
    else:
        raise Http404('Invalid visit.')
        #this_game = Game(name=name, size=size)
        #form = DirectionForm()
    state = this_game.state
    context = {
        'form':form,
        'name':name,
        'size':size,
        'game':this_game,
        'state':state,
        'direction':direction,
    }
    #print(this_game.board4print()) #TEST
    return render(request, 'Game_2048/playing.html', context)

def submit_score(request):
    print(get_ip_addr(request), 'visits submit score.') #TEST
    if not request.is_ajax():
        raise Http404('Invalid visit.')
    name = request.session.get('username')
    print('submit score:', name, request.POST) #TEST
    if name is None:
        raise Http404('Invalid user.')
    if request.method == 'POST':
        form = SubmitScoreForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data) #TEST
            context = {
                'name':name,
                'size':form.cleaned_data['size'],
                'score':form.cleaned_data['score'],
            }
            return render(request, 'Game_2048/submit_score.html', context)
    raise Http404('Invalid submission.')
