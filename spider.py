import re
from urllib.request import Request, urlopen
from collections import deque

queue = deque()
visited = set()

url = 'http://stackoverflow.com/'

queue.append(url)
cnt = 0

def judge_cur_link(link):
    flag = False

    if 'http' not in link:
        return flag
    if link in visited:
        return flag
    if link in queue:
        return flag

    flag = True
    return flag

def filter_link_list(link_list, visited, queue):
    for link in link_list:
        if judge_cur_link(link):
            queue.append(link)
        #  if 'http' in link:
            #  if link not in visited:
                #  if link not in queue:
                    #  queue.append(link)

while queue:
    url = queue.popleft()  # 队首元素出队
    visited |= {url}  # 标记为已访问
    # visited.update(url)  # 标记为已访问
    print('已经抓取: ',  cnt,'/',len(set(queue)),'   正在抓取 <---  ', url)
    cnt += 1

    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
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
    valid_list = filter_link_list(link_list, visited, queue)

print("抓取结束。")
