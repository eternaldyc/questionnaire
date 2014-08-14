#coding=utf-8
#!/usr/bin/python   
from datetime import date, datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate,login,logout


import os, sys
import json
import re
import urllib, urllib2

# 加载数据模型类
from polls.models import Choice, Poll, Userdata
import random

QUESION_NUM = 3

def get_question(poll_id): 
    '''抽题函数，输入为poll的数据库中的id，返回poll对象'''
    try:
        question = Poll.objects.filter(id=int(poll_id))[0]
        return question
    except Exception,e:
        print e
        raise Http404



def index(request, poll_id):
    try:
        latest_poll_list = Poll.objects.all().order_by('-pub_date')[:100] #此处的数字可以限制返回的个数
        question_list = random.sample(latest_poll_list, 3)
        num = len(latest_poll_list)
        print question_list
        poll = question_list[int(poll_id)]
    except Exception,e:
        print e
        raise Http404
    return render(request, 'polls/welcome.html', locals(), context_instance=RequestContext(request))

def questionnaire(request):
    if request.method.upper() == 'POST':
        if 'inputEmail' in request.POST: #只要从注册页面进行的post，自动按照新用户处理！
            if "user_id" in request.session:
                del request.session["user_id"]
            elif "user_progress" in request.session:
                del request.session["user_progress"]
            elif "question_number" in request.session:
                del request.session["question_number"]
            elif "question_id_list" in request.session:
                del request.session["question_id_list"]
        if "user_id" in request.session and "user_progress" in request.session: # 已经拿到系统分配的id
            user_id = request.session["user_id"]
            user_progress = request.session["user_progress"]
            question_max_number = request.session["question_number"]
            question_id_list = request.session["question_id_list"].split(',')
            current_question_id = int(request.POST['question_id'])
            if current_question_id == int(question_id_list[-1]): # 已经答完了最后一道题，跳转到结果页
                #处理结果！。。。
                # 待完善。。。
                #清空用户的session，下次访问算作另一个session
                del request.session["user_id"]
                del request.session["user_progress"]
                del request.session["question_number"] 
                del request.session["question_id_list"]
                # 上面是情况空session的操作
                return render(request, 'polls/result.html', locals(), context_instance=RequestContext(request))
            elif "choice" in request.POST: # 还没答完，记录本题答案，并且展现下一题
                # 获得基本信息
                print 'user_progress',user_progress
                print 'question_id_list[int(user_progress)-1]:', question_id_list[int(user_progress)-1]
                print 'question_id_list[int(user_progress)]:', question_id_list[int(user_progress)]
                if current_question_id == int(question_id_list[int(user_progress)-1]): # 证明用户重复提交，或在页面按了F5，不生成新题,不用保存用户数据！
                    print "F5!"
                    next_question_number = int(question_id_list[int(user_progress)])
                    request.session["user_progress"] = user_progress 
                    poll = get_question(next_question_number)
                    view_progress = 90.0*(user_progress)/(question_max_number) + 10.0 #认为完成注册了就完成了10%
                    return render(request, 'polls/questionnaire.html', locals(), context_instance=RequestContext(request))
                else: # 不是重复提交，保存选择，生成新题
                    user_choice = request.POST['choice'] 
                    question_id_list = request.session["question_id_list"].split(",")
                    current_question_number = int(question_id_list[int(user_progress)])
                    # 保存用户选择
                    UD = Userdata(user_id=user_id, info_type = current_question_number, info_content = user_choice , info_datetime=timezone.now())
                    UD.save()
                    # 生成新的题
                    user_progress = user_progress + 1
                    next_question_number = int(question_id_list[int(user_progress)])
                    request.session["user_progress"] = user_progress
                    poll = get_question(next_question_number)
                    view_progress = 90.0*(user_progress)/(question_max_number) + 10.0 #认为完成注册了就完成了10%
                    print next_question_number,question_max_number
                    return render(request, 'polls/questionnaire.html', locals(), context_instance=RequestContext(request))

                
        else: # 刚刚提交用户注册申请，还没有得到系统生成的user_id
            if 'inputEmail' in request.POST: # 这是正常的情况，else中的情况代表用户在最后一页刷新的情况
                user_email = request.POST['inputEmail'] #后面的空代表默认值
                user_age = request.POST['inputAge']
                user_gender = request.POST['inputGender']
                # 生成一个新的id，先查询数据库中最新的id
                last_id = Userdata.objects.all().order_by('-user_id')[1:1] #此处的数字可以限制返回的个数
                if last_id:
                    user_id = int(last_id[0]) + 1
                else:
                    user_id = 1
                # 将用户录入的信息合并成info_content
                user_info = user_email + '\t' + user_age + '\t' + user_gender
                UD = Userdata(user_id=user_id, info_type = -1, info_content = user_info , info_datetime=timezone.now())
                UD.save()
                #开始抽题
                try:
                    latest_poll_list = Poll.objects.all().order_by('-pub_date')[:100] #此处的数字可以限制返回的个数
                    print 'latest_poll_list:', latest_poll_list
                    question_list = random.sample(latest_poll_list, QUESION_NUM) # 抽3个题
                    print 'question_list:', question_list
                    question_id_list = map(lambda x: str(x.id) , question_list)
                    question_id_list.sort()
                    print 'question_id_list:',question_id_list
                except Exception,e:
                    print e
                    raise Http404
                request.session["user_id"] = user_id
                request.session["user_progress"] = 0
                request.session["question_number"] = QUESION_NUM
                request.session["question_id_list"] = ",".join(question_id_list)
                poll = get_question(question_id_list[0])
                view_progress = 10 #认为完成注册了就完成了10%
                print poll
                return render(request, 'polls/questionnaire.html', locals(), context_instance=RequestContext(request))
            else:
                return HttpResponseRedirect("/polls/")
    elif request.method.upper() == 'GET': # 不是post请求，不予理会，返回主页。
        try:
            latest_poll_list = Poll.objects.all().order_by('-pub_date')[:100] #此处的数字可以限制返回的个数
            question_list = random.sample(latest_poll_list, 3)
            num = len(latest_poll_list)
            print question_list
            poll = question_list[int(poll_id)]
        except Exception,e:
            print e
            raise Http404
        return render(request, 'polls/welcome.html', locals(), context_instance=RequestContext(request))

   
def detail(request, poll_id):
    try:
        poll = Poll.objects.get(pk=poll_id)
        # poll = get_object_or_404(Poll, pk=poll_id)
    except Poll.DoesNotExist:
        raise Http404
    return render(request, 'polls/detail.html', {'poll': poll})

def results(request, poll_id):

    return HttpResponse("You're looking at the results of poll %s." % poll_id)

def vote(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the poll voting form.
        return render(request, 'polls/detail.html', {
            'poll': p,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))