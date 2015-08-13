import re
import urllib.request
import urllib
from socket import timeout
from collections import deque

queue = deque()
visited = set()

url = 'http://news.dbanotes.net'  # 入口页面, 可以换成别的
# url = "http://lispinsummerprojects.org/completed-projects"
# url = 'http://www.yyets.com/resourcelist'  # 入口页面, 可以换成别的
# url = 'http://www.yyets.com/resource/29626'  # 入口页面, 可以换成别的
queue.append(url)
cnt = 0

while queue:
    url = queue.popleft()  # 队首元素出队
    visited |= {url}  # 标记为已访问
    # visited.update(url)  # 标记为已访问
    print('已经抓取: ',  cnt,'/',len(set(queue)),'   正在抓取 <---  ', url)
    cnt += 1

    try:
        urlop = urllib.request.urlopen(url, timeout=10)
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
    for link in link_list:
        # if 'http' in link and link not in visited:
        if 'http' in link:
            if link not in visited:
                if link not in queue:
                    queue.append(link)
            # print('加入队列 --->  ' + link)

print("抓取结束。")