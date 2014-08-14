# -*- coding: utf-8 -*- 
from django.contrib import admin
from polls.models import Choice, Poll, Userdata
# Register your models here.


# class ChoiceInline(admin.StackedInline):
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class PollAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['question']}), # None指的是没有框的标题
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}), #圆括号是标题和内容，内容在花括号里，域是内容，classes是修饰
    ] #内容细节的展示的自定义
    inlines = [ChoiceInline]
    list_display = ('question', 'pub_date', 'was_published_recently') #列表展示的自定义
    list_filter = ['pub_date'] # That adds a “Filter” sidebar that lets people filter the change list by the pub_date field
    search_fields = ['question'] # 搜索控件

admin.site.register(Poll, PollAdmin)

class UserDataAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['user_id']}), # None指的是没有框的标题
        ('Date information', {'fields': ['info_datetime'], 'classes': ['collapse']}), #圆括号是标题和内容，内容在花括号里，域是内容，classes是修饰
        ('info_type',               {'fields': ['info_type']}), 
        ('info_content',               {'fields': ['info_content']}), 
    ] #内容细节的展示的自定义

    list_display = ('user_id', 'info_type', 'info_content') #列表展示的自定义
    list_filter = ['info_datetime', 'info_type'] # That adds a “Filter” sidebar that lets people filter the change list by the pub_date field
    search_fields = ['user_id'] # 搜索控件
admin.site.register(Userdata, UserDataAdmin)