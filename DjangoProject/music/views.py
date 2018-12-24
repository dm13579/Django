from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, HttpResponse
from .models import Playlist, Commentsong, Commentsongsecond, Commentlikestates, Creategedan, Gedansong, DynamicPost, \
    Guanzhu, Commentdynamic
from .forms import CreategedanForm, DynamicForm
from django.contrib.auth.models import User
from .musicapi import search, getdetailsong, getlyric, getmp3con, getalbumdetail, load_mp3, hotrecommend, \
    newrecommend, rankinggedandetail, otheralbum, artistmvs, artistintroduce, playmv
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import re, json, datetime, time, datetime
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse
from django.utils.encoding import escape_uri_path
import gensim

# Create your views here.


@csrf_exempt
def searchlistmesssage(request):
    global searchlist, music_name;
    music_name = request.POST.get("musicname")
    songs = search(music_name, 1)
    searchlist= [[] for i in range(songs['result']['songCount'])]
    for num, song in enumerate(songs['result']['songs']):
        searchlist[num] = [song['id'], song['name'], song['artists'][0]['name'], song['album']['name'],
                     song['artists'][0]['id'], song['album']['id']]

    return render(request, "music/search_list.html", {"list": list})


# 搜索列表

@login_required(login_url='/account/login')
@csrf_exempt
def searchlist(request):
    paginator = Paginator(searchlist, 10)
    page = request.GET.get('page')
    try:
        current_page = paginator.page(page)
        music_list = current_page.object_list
    except PageNotAnInteger:
        current_page = paginator.page(1)
        music_list = current_page.object_list
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)
        music_list = current_page.object_list
    gedans = Creategedan.objects.filter(create_user=request.user)
    return render(request, 'music/search_list.html',
                  {"music_name": music_name, "length": len(searchlist), "list": music_list,
                   "page": current_page, "gedans": gedans})


@csrf_exempt
def albumlist(request):
    songs = search(music_name, 10)
    listalbum = [[] for i in range(songs['result']['albumCount'])]
    for num, album in enumerate(songs['result']['albums']):
        listalbum[num] = [album['id'], album['name'], album['blurPicUrl'], album['artist']['name'],
                          album['artist']['id']]
    paginator = Paginator(listalbum, 15)
    page = request.GET.get('page')
    try:
        current_page = paginator.page(page)
        list_album = current_page.object_list
    except PageNotAnInteger:
        current_page = paginator.page(1)
        list_album = current_page.object_list
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)
        list_album = current_page.object_list
    return render(request, 'music/album_list.html',
                  {"music_name": music_name, "length": len(listalbum), "listalbum": list_album, "page": current_page})


@csrf_exempt
def authorlist(request):
    songs = search(music_name, 100)
    listartist = [[] for i in range(songs['result']['artistCount'])]
    for num, artist in enumerate(songs['result']['artists']):
        listartist[num] = [artist['id'], artist['name'], artist['picUrl']]
    paginator = Paginator(listartist, 10)
    page = request.GET.get('page')
    try:
        current_page = paginator.page(page)
        list_artist = current_page.object_list
    except PageNotAnInteger:
        current_page = paginator.page(1)
        list_artist = current_page.object_list
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)
        list_artist = current_page.object_list
    return render(request, 'music/author_list.html', {"music_name": music_name, "length": len(listartist),
                                                      "listartist": list_artist, "page": current_page})


def mp3detail(request, id):
    data = getdetailsong(int(id))

    albumimgs = data['songs'][0]['album']['blurPicUrl']
    al = data['songs'][0]['album']['id']
    songname = data['songs'][0]['name']
    # 歌手处理
    artist = [[] for i in range(5)]
    for i, artists in enumerate(data['songs'][0]['artists']):
        artist[i] = [artists['name'], artists['id']]

    albumname = data['songs'][0]['album']['name']
    # 歌词处理
    lyric = getlyric(int(id))
    lrc = lyric['lrc']['lyric']
    regex = re.compile(r'\[.*\]')
    final_lrc = re.sub(regex, '', lrc).strip()
    # 评论获取,从userlist中对comentator进行筛选
    comment = Commentsong.objects.filter(music_id=id)
    userlist = User.objects.all()
    # 二级评论
    comment_second = Commentsongsecond.objects.all()
    # 已评论且为点赞用户
    comment_like = Commentlikestates.objects.filter(states='1')
    # 歌单
    gedan = Creategedan.objects.filter(create_user=request.user)
    print(gedan)
    return render(request, 'music/mp3detail.html', {
        "albumimgs": albumimgs, "songname": songname, "artist": artist,
        "albumname": albumname, "lyric": final_lrc, "id": id, "al": al,
        "comment": comment, "userlist": userlist, "comment_second": comment_second,
        "comment_like": comment_like, "gedan": gedan})


@csrf_exempt
def playmusic(request):
    try:
        id = request.POST.get("id")
        geturl = getmp3con(int(id))[0]['url']
        print(geturl)
        getimgcover = getdetailsong(int(id))['songs'][0]['album']['blurPicUrl']
        getmusicname = getdetailsong(int(id))['songs'][0]['name']
        # 首先查id判断是否有此歌曲，没有就添加进数据库，有就不添加，然后将数据库中内容传到ajax song
        # 中，用for循环构建song列表。
        # footer.html在页面每次刷新时取出数据库数据传到前端。(ajax取数据)
        u = Playlist.objects.filter(music_id=id, create_people=request.user)
        if len(u) == 0:
            Playlist.objects.get_or_create(music_id=id, music_name=getmusicname, music_albumimg=getimgcover,
                                           music_url=geturl, create_people=request.user,
                                           create_date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        else:
            Playlist.objects.filter(music_id=id).update(create_date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        # 查找数据库播放列所有歌曲
        list = Playlist.objects.filter(create_people=request.user).order_by("-create_date")
        # 把所有歌曲构造json（[{},{}...]）,并将其播放url更新（url会过期）
        footlist = [{} for i in range(list.count())]
        for num in range(list.count()):
            # geturl = getmp3con(int(list[num].music_id))[0]['url']
            # Playlist.objects.filter(music_id=list[num].music_id).update(music_url=geturl)
            footlist[num] = {'cover': list[num].music_albumimg, 'src': list[num].music_url,
                             'title': list[num].music_name}
        return HttpResponse(json.dumps(footlist), content_type="application/json")
    except:
        return HttpResponse(json.dumps("2"), content_type="application/json")


@csrf_exempt
def footlist(request):
    list = Playlist.objects.filter(create_people=request.user).order_by("-create_date")
    footlist = [{} for i in range(list.count())]
    for num in range(list.count()):
        # geturl = getmp3con(int(list[num].music_id))[0]['url']
        # Playlist.objects.filter(music_id=list[num].music_id).update(music_url=geturl)
        footlist[num] = {'cover': list[num].music_albumimg, 'src': list[num].music_url, 'title': list[num].music_name, 'id': list[num].music_id}

    return HttpResponse(json.dumps(footlist), content_type="application/json")


# 歌手详情（爬虫实现非api）
def artistdetail(request, ar, name):
    # 歌手个人信息
    information = artistintroduce(int(ar))["introduction"]
    informationlist = [[] for i in range(len(information))]
    for num, info in enumerate(information):
        informationlist[num] = info['ti'], info['txt']

    # 歌手其他MV
    mvs = artistmvs(int(ar))["mvs"]
    mvslist = [[] for i in range(len(mvs))]
    for num, info in enumerate(mvs):
        mvslist[num] = info['id'], info['name'], info['imgurl']

    paginator = Paginator(mvslist, 10)
    page = request.GET.get('page')
    try:
        current_page = paginator.page(page)
        mvslist = current_page.object_list
    except PageNotAnInteger:
        current_page = paginator.page(1)
        mvslist = current_page.object_list
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)
        mvslist = current_page.object_list
    return render(request, "music/artistdetail.html",
                  {"name": name, "informationlist": informationlist, "mvslist": mvslist, "page": current_page})


@csrf_exempt
def play_mv(request):
    # 240可换480 720 1080 清晰度
    data = playmv(int(request.POST.get("mv_id")))["data"]['brs']["240"]
    return HttpResponse(json.dumps(data))


def albumdetail(request, al):
    data = getalbumdetail(al)['album']
    list = [{} for i in range(len(data['songs']))]

    for num, song in enumerate(data['songs']):
        songartist = [[] for i in range(len(song['artists']))]
        for i, artists in enumerate(song['artists']):
            songartist[i] = [artists['name'], artists['id']]
        list[num] = [song['name'], song['id'], songartist]

    blurpicUrl = data['blurPicUrl']
    company = data['company']
    album_name = data['name']

    publishtime = data['publishTime']
    timestamp = float(publishtime / 1000)
    timearray = time.localtime(timestamp)
    styletime = time.strftime("%Y-%m-%d", timearray)

    artist = [[] for i in range(len(data['artists']))]
    for i, artists in enumerate(data['artists']):
        artist[i] = [artists['name'], artists['id']]

    gedan = Creategedan.objects.filter(create_user=request.user)
    return render(request, "music/albumdetail.html",
                  {"list": list, "blurpicUrl": blurpicUrl, "company": company, "album_name": album_name,
                   "publishtime": styletime, "artist": artist, "len": len(list), "gedan": gedan})


@csrf_exempt
def download_mp3(request,id,name):
    try:
        geturl = getmp3con(int(id))[0]['url']
        message = load_mp3(geturl, name)
        the_file_name=name+'.mp3'  
        filename='/DjangoProject/static/media/musicdownload/'+the_file_name    
        file=open(filename,'rb')
        response=StreamingHttpResponse(file)
        response['Content-Type']='application/octet-stream'
        response['Content-Disposition']='attachment;filename=''{}'.format(escape_uri_path(the_file_name))
        return response
    except:
        return render(request,"music/message.html")
 

@csrf_exempt
def comment_song(request):
    id = request.POST.get("id")
    body = request.POST.get("body")
    user_name = request.user
    Commentsong.objects.create(music_id=id, commentator=user_name, body=body)

    return HttpResponse(json.dumps("success"), content_type="application/json")


@csrf_exempt
def comment_song_second(request):
    commentator_id = request.POST.get("id")
    body = request.POST.get("body")
    comment_song_id = Commentsong.objects.get(id=commentator_id)
    Commentsongsecond.objects.create(commentator=comment_song_id, huifupeople=request.user, body=body)
    return HttpResponse(json.dumps("success"), content_type="application/json")


@csrf_exempt
def comment_like(request):
    id = request.POST.get("id")
    comment = Commentsong.objects.get(id=id)
    u = Commentlikestates.objects.filter(commentator_id=comment.id, dianzanuser=request.user.username)
    if len(u) > 0:
        cstates = Commentlikestates.objects.get(commentator_id=comment.id, dianzanuser=request.user.username)
        if cstates.states == '0':
            a = int(comment.like)
            comment.like = a + 1
            comment.save()
            cstates.states = 1
            cstates.save()
            result = {'state': True, 'msg': comment.like}
        else:
            a = int(comment.like)
            comment.like = a - 1
            comment.save()
            cstates.states = 0
            cstates.save()
            result = {'state': False, 'msg': comment.like}
    else:
        Commentlikestates.objects.create(commentator=comment, states=1, dianzanuser=request.user.username)
        a = int(comment.like)
        comment.like = a + 1
        comment.save()
        result = {'state': True, 'msg': comment.like}
    return HttpResponse(json.dumps(result), content_type="application/json")


@login_required(login_url='/account/login')
@csrf_exempt
def mymusic(request, id):
    if request.method == "GET":
        gedans = Creategedan.objects.filter(create_user=request.user)
        gedan_form = CreategedanForm()

        # 筛选出登录用户所收藏的歌曲，多对多
        user = User.objects.get(username=request.user.username)
        shougedans = user.gedan_like.all()
        if int(id) > 0:
            gedan = Creategedan.objects.get(id=id)
            return render(request, "music/mymusic.html",
                          {"gedan": gedan, "shougedans": shougedans, "gedans": gedans, 'gedan_form': gedan_form})
        else:
            gedan = Creategedan.objects.filter(create_user=request.user).first()
            return render(request, "music/mymusic.html",
                          {"gedan": gedan, "shougedans": shougedans, "gedans": gedans, 'gedan_form': gedan_form})
    elif request.method == "POST":
        gedan_name = request.POST.get("gedan_name")
        columns = Creategedan.objects.filter(create_user=request.user, gedanname=gedan_name)
        if columns:
            return HttpResponse("2")
        else:
            Creategedan.objects.create(create_user=request.user, gedanname=gedan_name)
            return HttpResponse("1")


@csrf_exempt
def shoucangmusic(request):
    id = request.POST.get("id")
    gedan_name = request.POST.get("gedanname")
    gedan = Creategedan.objects.get(create_user=request.user, gedanname=gedan_name)
    getmusicname = getdetailsong(int(id))['songs'][0]['name']
    getimgcover = getdetailsong(int(id))['songs'][0]['album']['blurPicUrl']
    data = getdetailsong(int(id))
    artist = data['songs'][0]['artists'][0]['name']
    artist_id = data['songs'][0]['artists'][0]['id']

    albumname = data['songs'][0]['album']['name']
    album_id = data['songs'][0]['album']['id']
    c = Gedansong.objects.filter(gedan=gedan, music_id=id)
    if c:
        return HttpResponse("2")
    else:
        Gedansong.objects.create(gedan=gedan, music_id=id, music_name=getmusicname, music_albumimg=getimgcover,
                                 music_artist=artist, music_artist_id=artist_id, music_album=albumname,
                                 music_album_id=album_id)
        return HttpResponse("1")

@login_required(login_url='/account/login')
@csrf_exempt
def myroom(request):
    photo = request.user.userprofile.photo

    if request.user.userprofile.birth:
        birth = request.user.userprofile.birth
        birth_year = birth.strftime('%Y')
        now_year = datetime.datetime.now().strftime('%Y')
        age = int(now_year) - int(birth_year)
    else:
        age = "未知"
    creategedan = Creategedan.objects.filter(create_user=request.user)

    shougedans = request.user.gedan_like.all()
    playlist = Playlist.objects.filter(create_people=request.user).order_by("-create_date")
    return render(request, 'music/myroom.html',
                  {"photo": photo, "age": age, "creategedan": creategedan, "shougedans": shougedans, "playlist": playlist})

@login_required(login_url='/account/login')
@csrf_exempt
def otherinfo(request, user_id):
    otheruser = User.objects.get(id=user_id)
    photo = otheruser.userprofile.photo

    if otheruser.userprofile.birth:
        birth = otheruser.userprofile.birth
        birth_year = birth.strftime('%Y')
        now_year = datetime.datetime.now().strftime('%Y')
        age = int(now_year) - int(birth_year)
    else:
        age = "未知"
    creategedan = Creategedan.objects.filter(create_user=otheruser)

    # 筛选出登录用户所收藏的歌曲，多对多
    shougedans = otheruser.gedan_like.all()
    return render(request, 'music/otherinfo.html',
                  {"otheruser": otheruser, "photo": photo, "age": age, "creategedan": creategedan,
                   "shougedans": shougedans})

@login_required(login_url='/account/login')
def gedandetail(request, gedan_id):
    gedan = Creategedan.objects.get(id=gedan_id)
    gedans = Creategedan.objects.filter(create_user=request.user)
    return render(request, "music/gedandetail.html", {"gedan": gedan, "gedans": gedans})


@csrf_exempt
def shoucanggedan(request):
    gedan_id = request.POST.get("id")
    status = request.POST.get("status")
    gedan = Creategedan.objects.get(id=gedan_id)
    if status == "shou":
        gedan.user_like.add(request.user)
        return HttpResponse("1")
    elif status == "delete":
        gedan.user_like.remove(request.user)
        return HttpResponse("1")
    return HttpResponse("0")

@login_required(login_url='/account/login')
def mydynamic(request):
    # 你所关注的人
    myguanpeoples = Guanzhu.objects.filter(guangzhufor=request.user)
    # 所有的动态
    dy_all = DynamicPost.objects.all().order_by("-created")
    guan_list = [[] for i in range(dy_all.count())]
    i = 0
    # 将你所关注的人的所有动态全部存入list中
    for dy in dy_all:
        m = myguanpeoples.filter(guangzhuto=dy.author_id)
        if m.count() > 0:
            use = User.objects.get(id=dy.author_id)
            guan_list[i] = dy, use
            i = i + 1
    # 自己所发送的所有动态
    my_dynamic = DynamicPost.objects.filter(author=request.user)

    myguanzhuall = Guanzhu.objects.all()
    fensi = [[] for i in range(myguanzhuall.count())]
    i = 0
    for my_all in myguanzhuall:
        my_user = User.objects.get(username=my_all.guangzhuto)
        fensi[i] = my_user.guanzhuto.count(), my_user
        i = i + 1
    print(fensi)   
    quchong=list(set(fensi))
    dysort = DynamicPost.objects.all().order_by("-likes")
    quchong.sort(key=lambda x: x[0], reverse=True)
    return render(request, "music/mydynamic.html", {"my_dynamic": my_dynamic,
                                                    "guan_list": guan_list, "list_fensi": quchong[:4],
                                                    "dysort": dysort})


@csrf_exempt
def dynamic_comment(request):
    dynamicpost = DynamicPost.objects.get(id=request.POST.get("dynamic_id"))
    id = request.POST.get("id")
    body = request.POST.get("body")
    Commentdynamic.objects.create(comment_dynamic=dynamicpost, commentator=request.user, body=body)
    return HttpResponse("1")


@csrf_exempt
def mydynamic_save(request):
    DynamicPost.objects.create(author=request.user, body=request.POST.get("body"))
    return HttpResponse("1")


@csrf_exempt
def mydynamic_like(request):
    dynamic_id = request.POST.get("dynamic_id")
    dynamic = DynamicPost.objects.get(id=dynamic_id)
    status = request.POST.get("status")
    if status == 'zan':
        dynamic.user_like.add(request.user)
        a = int(dynamic.likes)
        dynamic.likes = a + 1
        dynamic.save()
        return HttpResponse(json.dumps(dynamic.likes))
    elif status == 'cancel':
        dynamic.user_like.remove(request.user)
        a = int(dynamic.likes)
        dynamic.likes = a - 1
        dynamic.save()
        return HttpResponse(json.dumps(dynamic.likes))


def mydynamic_layer(request):
    return render(request, "music/mydynamic_layer_frame.html")


@csrf_exempt
def guanzhu(request):
    otheruser = User.objects.get(id=request.POST.get("otheruser_id"))
    u = Guanzhu.objects.filter(guangzhufor=request.user, guangzhuto=otheruser)
    if u.count() == 0:
        Guanzhu.objects.create(guangzhufor=request.user, guangzhuto=otheruser)
        return HttpResponse("1")
    else:
        if request.POST.get("status") == "cancel":
            u.delete()
            return HttpResponse("3")
        return HttpResponse("2")


@login_required(login_url='/account/login')
def dynamic_detail(request, user_id):
    otheruser = User.objects.get(id=user_id)
    photo = otheruser.userprofile.photo

    if otheruser.userprofile.birth:
        birth = otheruser.userprofile.birth
        birth_year = birth.strftime('%Y')
        now_year = datetime.datetime.now().strftime('%Y')
        age = int(now_year) - int(birth_year)
    else:
        age = "未知"
    # 自己所发送的所有动态
    my_dynamic = DynamicPost.objects.filter(author=otheruser).order_by("-created")
    return render(request, "music/dynamic_detail.html",
                  {"otheruser": otheruser, "photo": photo, "age": age, "my_dynamic": my_dynamic})


@login_required(login_url='/account/login')
def fensi_detail(request, user_id):
    otheruser = User.objects.get(id=user_id)
    photo = otheruser.userprofile.photo

    if otheruser.userprofile.birth:
        birth = otheruser.userprofile.birth
        birth_year = birth.strftime('%Y')
        now_year = datetime.datetime.now().strftime('%Y')
        age = int(now_year) - int(birth_year)
    else:
        age = "未知"
    return render(request, "music/fensi_detail.html", {"otheruser": otheruser, "photo": photo, "age": age})


@login_required(login_url='/account/login')
def guan_detail(request, user_id):
    otheruser = User.objects.get(id=user_id)
    photo = otheruser.userprofile.photo

    if otheruser.userprofile.birth:
        birth = otheruser.userprofile.birth
        birth_year = birth.strftime('%Y')
        now_year = datetime.datetime.now().strftime('%Y')
        age = int(now_year) - int(birth_year)
    else:
        age = "未知"
    return render(request, "music/guan_detail.html", {"otheruser": otheruser, "photo": photo, "age": age})


# 主页

@login_required(login_url='/account/login')
def home(request):
    hotcommend = hotrecommend()["result"]
    hotcommendlist = [[] for i in range(len(hotcommend))]
    for num, gedan in enumerate(hotcommend):
        hotcommendlist[num] = gedan['id'], gedan['name'], gedan['picUrl']

    newcommend = newrecommend()["recommend"]
    newcommendlist = [[] for i in range(len(newcommend))]
    for num, gedan in enumerate(newcommend):
        newcommendlist[num] = gedan['id'], gedan['name'], gedan['picUrl']
    return render(request, "home.html", {"hotcommendlist": hotcommendlist, "newcommendlist": newcommendlist})

@login_required(login_url='/account/login')
def ranking(request, ranking_id):
    detail = rankinggedandetail(int(ranking_id))["result"]["tracks"]
    rankinglist = [[] for i in range(len(detail))]
    for num, song in enumerate(detail):
        rankinglist[num] = song['id'], song['name'], song['artists'][0]['id'], song['artists'][0]['name'], \
                           song["album"]['id'], song["album"]['name'], num + 1

    paginator = Paginator(rankinglist, 10)
    page = request.GET.get('page')
    try:
        current_page = paginator.page(page)
        rankinglist = current_page.object_list
    except PageNotAnInteger:
        current_page = paginator.page(1)
        rankinglist = current_page.object_list
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)
        rankinglist = current_page.object_list
    gedans = Creategedan.objects.filter(create_user=request.user)
    return render(request, "music/ranking.html", {"ranking_id": ranking_id, "rankinglist": rankinglist,
                                                  "page": current_page, "gedans": gedans})

@login_required(login_url='/account/login')
def hot_gedan(request):
    gedanall = Creategedan.objects.filter()

    li_gedan = [[] for i in range(gedanall.count())]
    i = 0
    for gedan in gedanall:
        li_gedan[i] = gedan.user_like.count(), gedan
        i = i + 1
    print(li_gedan)
    li_gedan_quchong = list(set(li_gedan))
    li_gedan_quchong.sort(key=lambda x: x[0], reverse=True)
    return render(request, "music/hot_gedan.html", {"li_gedan_quchong": li_gedan_quchong[:10]})

@login_required(login_url='/account/login')
def system_gedan(request, gedan_id):
    detail = rankinggedandetail(int(gedan_id))['result']['tracks']

    gedanlist = [[] for i in range(len(detail))]
    for num, song in enumerate(detail):
        gedanlist[num] = song['id'], song['name'], song['artists'][0]['id'], song['artists'][0]['name'], \
                         song["album"]['id'], song["album"]['name'], num + 1

    paginator = Paginator(gedanlist, 10)
    page = request.GET.get('page')
    try:
        current_page = paginator.page(page)
        gedanlist = current_page.object_list
    except PageNotAnInteger:
        current_page = paginator.page(1)
        gedanlist = current_page.object_list
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)
        gedanlist = current_page.object_list

    gedans = Creategedan.objects.filter(create_user=request.user)
    return render(request, "music/system_gedan.html", {"gedanlist": gedanlist, "page": current_page, "gedans": gedans})


@csrf_exempt
def gedan_chuli(request):
    id = request.POST.get("id")
    status = request.POST.get("status")
    if status == "edit":
        new_name = request.POST.get("new_name")
        if Creategedan.objects.filter(gedanname=new_name, create_user=request.user):
            return HttpResponse("2")
        else:
            obj = Creategedan.objects.get(id=id)
            obj.gedanname = new_name
            obj.save()
            return HttpResponse("1")
    elif status == "delete":
        Creategedan.objects.filter(id=id).delete()
        return HttpResponse("3")
    elif status == "deletesong":
        Gedansong.objects.filter(id=id).delete()
        return HttpResponse("4")


@csrf_exempt
def del_play(request):
    Playlist.objects.filter(id=request.POST.get("id")).delete()
    return HttpResponse("1")


def xiangsi_detail(request, song_id):
    try:
        # 载入model
        model = gensim.models.Word2Vec.load('static/songVec.model')
        songname = getdetailsong(int(song_id))['songs'][0]['name']
        result_song_list = model.most_similar(song_id)
        simsong = list()
        for song in result_song_list:
            simsong.append(song[0])
        gelist = [[] for i in range(len(simsong))]
        num = 0
        for song in simsong:
            song = getdetailsong(int(song))['songs'][0]
            gelist[num] = song['id'], song['name'], song['artists'][0]['id'], song['artists'][0]['name'], \
                             song["album"]['id'], song["album"]['name'], num + 1
            num = num+1
    except:
        hotcommend = hotrecommend()["result"][0]['id']
        detail = rankinggedandetail(int(hotcommend))['result']['tracks']
        gelist = [[] for i in range(len(detail))]
        for num, song in enumerate(detail):
            gelist[num] = song['id'], song['name'], song['artists'][0]['id'], song['artists'][0]['name'], \
                             song["album"]['id'], song["album"]['name'], num + 1
    gedans = Creategedan.objects.filter(create_user=request.user)
    return render(request, "music/xiangsi.html", {"gelist": gelist[:10], "gedans": gedans, "songname": songname})

