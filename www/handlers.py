#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

' url handlers '

import re, time, json, logging, hashlib, base64, asyncio

from coroweb import get, post, get_required_kw_args

# from models import User, Comment, Blog, next_id
from apis import Page

import os,random

from blogsearch import bs

def get_item(docid):
    document = bs.documents[docid]

    head = '<div style="margin-top:100px; text-align:center; margin-bottom:20px" >' + '<h2><a href="' + document.link +'"   style="font-size:20px;line-height:32px; text-align:middle; text-decoration:none; color:#444">' + document.name + '</a></h2>' + '<p class="uk-article-meta" style="margin:20px 0">创建于 ' + document.year + '年' + document.month +'月 | 分类标签：'

    for tag in document.tags[:5]:
        head += '<a href="/search?q='+tag+'">'+tag+'</a>    '

    head += ' | 文章词数：' + str(document.num_words)
    head += '</p>' + '</div>'

    item_html = '        <div class="">\n'
    item_html += '            <div class="" >\n'
    item_html += head
    item_html += document.summary
    item_html += '<a class="uk-button" style="display:block;font-size:14px; width:100px; margin:auto; margin-top:40px" href="' + document.link +'">阅读全文》</a>'
    item_html += '            </div>\n'
    item_html += '        </div>\n'
    return item_html

def get_recent():
    recentid = []
    time_key = [k for k in bs.time_dict]
    time_key = sorted(time_key, reverse=True)
    for k in time_key:
        if len(recentid) >= 5:
            break
        recentid += bs.time_dict[k]
    recentid = recentid[:5]
    recent_content  = ''
    for docid in recentid:
        document = bs.documents[docid]
        recent_content += '<li><a href="' + document.link+'">' + document.name +'</a></li>'
    return recent_content

def get_tags_content(numtags=40):
    showtags = bs.sorted_tagdict[:numtags]
    maxv = showtags[0][1]/20
    random.shuffle(showtags)
    tags_content = ''
    for k,v in showtags:
        tags_content += '<a style="font-size:' +str(6+v/maxv) + 'pt;" href="/search?q=' + k +'">\t' + k +' </a>'
    return tags_content

def get_archives():
    archive_content = ''
    archives = [k for k in bs.time_dict]
    archives = sorted(archives, reverse=True)
    for k in archives:
        archive_content += '<h2>' + k +'</h2>'
        article_items = ''
        for v in bs.time_dict[k]:
            document = bs.documents[v]
            article_items += '<li><a href="' + document.link+'">' + document.name +'</a></li>'
        archive_content += article_items
    return archive_content

@get('/')
def index(*, page='1'):
    img = '<img class="" src="/static/img/background/book0.jpg" width="100%" height="" alt="" style="max-height:500px">'
    page_index = bs.current_page
    if page == 'next':
        page_index += 1
    elif page == 'prior':
        page_index -= 1
        page_index = max(page_index, 0)
    else:
        try:
            page_index = int(page)-1
        except Exception as e:
            raise

    bs.current_page = page_index

    docids = bs.get_page(page_index%bs.total_pages)
    while len(docids) < 3:
        x = random.randint(0,bs.total_docs)
        if x not in docids:
            docids.append(random.randint(0, bs.total_docs))

    html_content = ''
    for docid in docids:
        html_content += get_item(docid)

    return {
        '__template__': 'home.html',
        'img': img,
        'name':'Life Is Like A Boat!',
        'meta':'You make me wanna strain at the oars, and soon i can\'t see the shore.',
        'html_content': html_content
    }

@get('/blogs/{year}/{month}/{name}/')
def get_blog(year, month, name):
    document = bs.get_document(year, month, name)

    img = '<img class="" src="/static/img/background/book0.jpg" width="100%" height="" alt="" style="max-height:768px">'

    meta = '创建于 ' + year + '年' + month +'月' + ' | 文章词数：' + str(document.num_words)

    tags = '<p>'
    for tag in document.tags[:5]:
        tags += '<a class="uk-button" href="/search?q='+tag+'">'+tag+'</a>    '
    tags += '</p>'

    recommend_blogs = bs.get_recommend(document.docid)
    recommend_blogs.remove(document.docid)
    while len(recommend_blogs) < 3:
        x = random.randint(0,len(bs.documents))
        if x not in recommend_blogs:
            recommend_blogs.append(x)

    if len(recommend_blogs) > 3:
        recommend_blogs = recommend_blogs[:3]

    recommend_content = '<div class="uk-grid" data-uk-grid-margin="">'
    for docid in recommend_blogs:
        recommend_content += '    <div class="uk-width-medium-1-3 uk-row-first" onclick="window.location=\'' + bs.documents[docid].link +'\';" style="cursor: pointer;">'
        recommend_content += '    <div class="uk-panel uk-panel-box">'
        recommend_content += '<div class="uk-panel-badge uk-badge uk-badge-notification">' + str(docid) + '</div>'
        recommend_content += '    <h4 class="uk-panel-title" style="font-size:16px"><i class="uk-icon-bookmark"></i>' + bs.documents[docid].name + '</h4>'
        for tag in bs.documents[docid].tags[:20]:
            recommend_content += tag +' '
        recommend_content += '    </div>'
        recommend_content += '</div>'
    recommend_content += '</div>'


    return {
        '__template__': 'blog.html',
        'html_content': document.read_html(),
        'tags':tags,
        'name': name,
        'meta':meta,
        'img':img,
        'recommend_content': recommend_content,
    }

@get('/search')
def get_search(*,q):
    img = '<img class="" src="/static/img/background/book1.jpg" width="100%" height="" alt="" style="max-height:768px">'

    searchdocs = bs.search(q)
    name = '搜索“' + q + '”找到 ' + str(len(searchdocs)) +' 条结果'

    html_content = ''
    for docid in searchdocs:
        html_content += get_item(docid)

    return {
        '__template__': 'basic.html',
        'html_content': html_content,
        'img':img,
        'name': name,
        'meta':'Life is like a box of chocolate, you never know what you\'re gonna get next.'
    }

@get('/flush')
def index_flush():
    print('flush index')
    count = bs.flush()
    html_content = '<div style = "background-color:#ababaa;box-shadow:0px 0px 20px 2px #ababaa;"><h2 style="color:#fff" class="uk-text-center"> ' +'flush index add ' + str(count) +' blogs' '</h2></div>'
    return {
        '__template__': 'basic.html',
        'html_content': html_content,
        'name': 'flush',
        'archive_content' : get_archives(),
        'recent_content' : get_recent(),
        'tag_content' : get_tags_content()
    }

@get('/archives')
def archives():
    img = '<img class="" src="/static/img/background/book2.jpg" width="100%" height="" alt="" style="max-height:500px">'
    return {
        '__template__': 'archives.html',
        'img':img,
        'name':'Archives',
        'meta':'keep going!',
        'archive_content':get_archives(),
        'recent_content':get_recent(),
        'tag_content': get_tags_content()
    }

@get('/about')
def about():
    img = '<img class="" src="/static/img/background/jugg1_768-0.jpg" width="100%" height="" alt="" style="max-height:500px">'
    return {
        '__template__': 'about.html',
        'name':'About',
        'meta':'just about me',
        'img':img,
        'recent_content':get_recent(),
        'tag_content': get_tags_content()
    }


# @get('/manage/blogs/create')
# def manage_create_blog():
#     return {
#         '__template__': 'manage_blog_edit.html',
#         'id': '',
#         'action': '/api/blogs'
#     }

# @get('/manage/blogs')
# def manage_blogs(*, page='1'):
#     return {
#         '__template__': 'manage_blogs.html',
#         'page_index': get_page_index(page)
#     }

# @get('/api/users')
# async def api_get_users():
#     users = await User.findAll(orderBy='created_at desc')
#     for u in users:
#         u.passwd = '******'
#     return dict(users=users)

# @get('/api/blogs')
# async def api_blogs(*, page='1'):
#     page_index = get_page_index(page)
#     num = await Blog.findNumber('count(id)')
#     p = Page(num, page_index)
#     if num == 0:
#         return dict(page=p, blogs=())
#     blogs = await Blog.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
#     return dict(page=p, blogs=blogs)

# @post('/api/blogs')
# async def api_create_blog(request, *, name, summary, content):
#     if not name or not name.strip():
#         raise APIValueError('name', 'name cannot be empty.')
#     if not summary or not summary.strip():
#         raise APIValueError('summary', 'summary cannot be empty.')
#     if not content or not content.strip():
#         raise APIValueError('content', 'content cannot be empty.')
#     blog = Blog(user_id=0, user_name="sharix", user_image="about:blank", name=name.strip(), summary=summary.strip(), content=content.strip())
#     await blog.save()
#     return blog
