import re
from urllib.request import Request, urlopen
from collections import deque


page_list = deque()
visited = set()

for i in range(1, 10):
    url = str.format("http://stackoverflow.com/questions?page={0}&sort=newest", i)
    page_list.append(url)


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
        print(str.format("正在抓取第{0}页/第{1}题, <--- {2}", page+1, cnt, url))

print("抓取结束。")
