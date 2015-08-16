import re
import goslate
import requests
from collections import deque
from urllib.request import Request, urlopen


page_list = deque()
visited = set()

for i in range(1, 2):
    url = str.format("http://stackoverflow.com/questions?page={0}&sort=newest", i)
    page_list.append(url)

page_list = ["http://stackoverflow.com/questions/11227809/why-is-processing-a-sorted-array-faster-than-an-unsorted-array"]

def judge_cur_link(link, visited):
    is_question = False
    if 'questions' not in link:
        return is_question
    if link in visited:
        return is_question
    if link in page_list:
        return is_question
    if len(link.split('/')) < 3:
        return is_question

    splited = link.split('/')
    for i, part in enumerate(splited):
        if part.isdigit():
            if splited[i - 1] == "questions":
                is_question = True

    return is_question

def filter_link_list(link_list, visited):
    valid_list = []
    for link in link_list:
        if judge_cur_link(link, visited):
            if len(link.split('/')) == 4:
                link = "http://stackoverflow.com" + link
            valid_list.append(link)
    return valid_list

def grep_question(url):
    response = requests.get(url)
    html_str = response.text
    html_str = html_str.split('<td class="postcell">')
    question = html_str[1].split('</td>')[0]
    question = question.split('<div class="post-text" itemprop="text">')
    question = question[1].split('</div>')[0]
    return question

def grep_tags(url):
    response = requests.get(url)
    html_str = response.text
    html_str = html_str.split('<div class="post-taglist">')
    html_str = html_str[1].split('</div>')[0]
    tag_re = re.compile('>(.+?)</a>')
    tag_list = tag_re.findall(html_str)
    return tag_list

def grep_answers(url):
    response = requests.get(url)
    html_str = response.text
    answers = html_str.split('<td class="answercell">')
    answer_list = []
    for i in range(1, len(answers)):
        per_ans = answers[i].split('</td>')[0]
        per_ans = per_ans.split('<div class="post-text" itemprop="text">')
        per_ans = per_ans[1].split('</div>')[0]
        answer_list.append(per_ans)
    return answer_list

def str_trans(str_en):
    gs = goslate.Goslate()
    str_zh = gs.translate(str_en, 'zh-CN')
    return str_zh

for page, node_url in enumerate(page_list):

    try:
        req = Request(node_url, headers={'User-Agent': 'Mozilla/5.0'})
        urlop = urlopen(req)
    except:
        print("HTTP Error 403: Forbidden")
        continue

    header = urlop.getheader('Content-Type')

    try:
        if 'html' not in header:
            print("It's not a html.")
            continue
    except:
        print("It's not a html.")
        continue

# 避免程序异常中止, 用try..catch处理异常
    try:
        data = urlop.read().decode('utf-8')
    except:
        print("Not utf-8.")
        continue

# 正则表达式提取页面中所有队列, 并判断是否已经访问过, 然后加入待爬队列
    linkre = re.compile('href=\"(.+?)\"')
    link_list = linkre.findall(data)
    valid_list = filter_link_list(link_list, visited)

    cnt = 0
    for url in valid_list:
        cnt += 1
        visited |= {url}  # 标记为已访问
        print(str.format("正在抓取第{0}页/第{1}题\t <--- {2}", page+1, cnt, url))

        # 解析问题页面的html
        question = grep_question(url)
        tag_list = grep_tags(url)
        answer_list = grep_answers(url)
        print(question)
        print('---------------------------------------\n')

        #  question_zh = str_trans(question_html)
        #  print(question_zh)

        break

print("抓取结束。")
