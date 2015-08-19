import re
import bs4
import goslate
import requests
from collections import deque
from urllib.request import Request, urlopen


page_list = deque()
visited = set()

for i in range(1, 2):
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

def grep_title(url):
    title_dash = url.split('/')[-1]
    title = title_dash.replace('-', ' ')
    return title

def title_trans(title_en, keep_en):
    gs = goslate.Goslate()
    title_zh = gs.translate(title_en, 'zh')
    title_html = ''
    if keep_en:
        title_zh_h1 = str.format("<h1>{0}</h1>", title_zh)
        title_en_h2 = str.format("<h2>{0}</h2>", title_en)
        title_html = title_zh_h1 + title_en_h2
    else:
        title_html = str.format("<h1>{0}</h1>", title_zh)
    return title_html

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

def html_trans(html_en, keep_en):
    gs = goslate.Goslate()

    # html 2 soup
    soup = bs4.BeautifulSoup(html_en, "html.parser")

    # save all code blocks
    code_list = soup.find_all('code')

    # drop tags of html, just save pure text
    text_en = soup.text

    # replace all code blocks to non-sense text
    for code in code_list:
        text_en = text_en.replace(code.text, "edocsiereh")

    # trans en to zh for pure text
    text_zh = gs.translate(text_en, 'zh')

    # split en pure text by non-sense text used above
    text_zh = text_zh.split("edocsiereh")

    # split zh pure text by non-sense text used above
    text_en = text_en.split("edocsiereh")

    # recover pure text to html again
    for i,zh in enumerate(text_zh):
        if keep_en:
            en = text_en[i]
            text_zh[i] = str.format("<p>{0}<br>{1}</p>", en, zh)
        else:
            text_zh[i] = str.format("<p>{0}</p>", zh)

    # add <pre> tag before <code>, otherwise code be shown strange
    for i,code in enumerate(code_list):
        code_list[i] = str.format("<pre>{0}</pre>", code)

    # insert code into text html
    for i,code in enumerate(code_list):
        text_zh.insert(i*2+1, code)

    # change list into just one long string
    html_zh = ""
    for text in text_zh:
        html_zh += str(text)

    # change new zh html string into soup
    soup_zh = bs4.BeautifulSoup(html_zh, "html.parser")

    # format the html
    html_zh = soup_zh.prettify(formatter="html")

    return html_zh

def html_list_trans(html_list_en):
    html_list_zh = []
    for html_en in html_list_en:
        html_zh = html_trans(html_en, False)
        html_list_zh.append(html_zh)
    return html_list_zh

def part_to_full_html(part):
    soup = bs4.BeautifulSoup(part, "html.parser")
    full_html = soup.prettify(formatter="html")
    print(full_html)
    return full_html

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
        #  print(str.format("正在抓取第{0}页/第{1}题\t <--- {2}", page+1, cnt, url))

        #  url = "http://stackoverflow.com/questions/11227809/why-is-processing-a-sorted-array-faster-than-an-unsorted-array"

        # Grep En Info
        title_en = grep_title(url)
        answer_list_en = grep_answers(url)
        question_html_en = grep_question(url)

        # Grep Question Tags List
        tag_list = grep_tags(url)

        # En to Zh Translation
        title_html_zh = title_trans(title_en, True)
        question_html_zh = html_trans(question_html_en, False)
        answer_list_zh = html_list_trans(answer_list_en)

        print(title_html_zh)
        print('Tags:', tag_list)
        print(question_html_zh)
        for i,answer in enumerate(answer_list_zh):
            print('Answer', i, '----------------------------------------------------------------')
            print(answer)

        if cnt > 2:
            break

#  print("抓取结束。")
