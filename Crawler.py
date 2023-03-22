# file_name:Crawler.py
import requests
import lxml
import bs4
import datetime
from lxml import etree
from bs4 import BeautifulSoup


error_address = []
error_content = []
title_list = []


def download_content(url):
    """
    第一个函数，用来下载网页，返回网页内容
    参数 url 代表所要下载的网页网址。
    整体代码和之前类似
    """
    response = requests.get(url)
    html = response.text
    return html


def save_to_file(filename, content):
    """
        会覆盖掉文件中现有的内容
        第二个函数，将字符串内容保存到文件中
        第一个参数为所要保存的文件名，第二个参数为要保存的字符串内容的变量
    """
    with open(filename, mode="w", encoding="gbk") as f:
        f.write(content)


def append_to_file(filename, content):
    """
        类似于save_to_file函数,但是不同于这个函数的地方在于,不会覆盖当前文件中的内容
        第二个函数，将字符串内容保存到文件中
        第一个参数为所要保存的文件名，第二个参数为要保存的字符串内容的变量
    """
    with open(filename, mode="a", encoding="gbk") as f:
        f.write(content)


def create_doc_from_filename(filename):
    # 输入参数为要分析的 html 文件名，返回值为对应的 BeautifulSoup 对象
    with open(filename, "r", encoding='gbk') as f:
        html_content = f.read()
        soup = BeautifulSoup(html_content, "lxml")
    return soup


def parse(soup, filename):
    """
    筛选出如下格式内容,并提取信息, 返回True说明时间范围内的条目已经全部扫完
    <tr>
        <td class="xmc_lp20"><a href="http://muchong.com/t-15595024-1" target="_blank" class="xmc_ft12">上海工程技术大学 化学 制药 化工 调剂（必须为08开头且考数学）</a>
        </td>
        <td>上海工程</td>学校
        <td>工学   </td>专业
        <td>2</td>
        <td>2023-03-08 20:26</td>
    </tr>
    """
    whole_post = ""
    a_post = ""
    post_list = soup.select(".forum_body_manage > tr")
    is_end = False
    flag = True
    for post in post_list:
        for child in post.children:
            if type(child) != bs4.element.NavigableString:
                # 内容非空
                if len(child.attrs)>0:
                    address = child.contents[0].attrs['href']
                    title = child.contents[0].string
                    # 如果标题已经存在,则跳过这个帖子,否则将标题加入列表
                    if title in title_list:
                        flag = False
                        break
                    else:
                        title_list.append(title)
                    # 记录帖子的 网址 和 标题
                    a_post = address + '\n' + title + '\n'
                    # 根据网址爬取具体内容, 返回值flag 为 True 则需要收集
                    flag = parse_post(address)
                else:
                    content = child.string
                    if content != None:
                        # 记录帖子的 其他信息(学校、专业、招收人数、帖子时间)
                        a_post = a_post + content + '\n'
                        # 确保查找的帖子都是昨天中午11点半之后的
                        # 异常处理用来找时间,如果不是时间就会抛出异常,但是这里不处理异常,是时间就会进行判断
                        try:
                            post_time = datetime.datetime.strptime(content, '%Y-%m-%d %H:%M')
                            yesterday = datetime.date.today() + datetime.timedelta(days=-1)
                            deadline = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 11, 30)
                            delta = post_time - deadline
                            if (delta.days*86400 + delta.seconds) < 0:
                                is_end = True
                        except ValueError:
                            pass
                    # 如果超出了逾期时间,就不再往后爬取
                    if is_end:
                        break
        if is_end:
            break
        if flag:
            whole_post = whole_post + a_post + '\n'
            print(whole_post)
    append_to_file(filename, whole_post)
    return is_end
    # print(whole_post)


def parse_post(address):
    """
    解析具体的帖子页面,主要获取 补充内容 部分
    当该帖子中存在关键字时,返回True,否则返回False
    """
    html = download_content(address)
    if(html == ""):
        print("当前网址内容获取失败: ", address)
        return False
    soup = BeautifulSoup(html, "lxml")
    post_content_list = soup.select('tbody#pid1 > tr.pls_mind > td.plc_mind')
    #print("post_content_list[0]: ", post_content_list[0])
    try:
        content_soup = BeautifulSoup(str(post_content_list[0]), "lxml")
    except IndexError:
        print("当前网址内容获取失败: ", address)
        print("post_content_list:", post_content_list)
        error_address.append(address)
        error_content.append(post_content_list)
        return False
    # 主要信息
    main_content = content_soup.select('div.forum_Mix > div > table')
    # 补充信息
    additional_content = content_soup.select('div.t_fsz > table > tr > td')
    #print("additional_content: ", additional_content)
    # 获取文本
    add_c = additional_content[0].text
    # 判断内容
    key_word = ["计算机", "计科", "计算机技术", "计算机科学与技术", "软件工程", "软工", "网络安全", "网安", "0812", "0854", "机器学习", "大数据"]
    for word in key_word:
        if add_c.find(word)>=0:
            return True
    return False


def run():
    # 下载报考指南的网页
    param = "?&page="
    url = "http://muchong.com/bbs/kaoyan.php"
    page = 1
    while True:
        if page > 1:
            full_url = url + param + str(page)
        else:
            full_url = url
        filename = "muchong_tiaoji.html"
        result_file = "考研调剂数据.txt"
        result = download_content(full_url)
        soup = BeautifulSoup(result, "lxml")
        is_end = parse(soup, result_file)
        if is_end:
            break
        page = page + 1
        # parse_post("http://muchong.com/t-15594937-1")
    print("work finished!")
    # 记录之前遇到的所有错误
    print("current error items:")
    for i in range(len(error_address)):
        print("出错网址: ", error_address[i])
        print("出错内容: ", error_content[i])


def test():
    parse_post("http://muchong.com/t-15604119-1")

def main():
    run()


if __name__ == '__main__':
    main()
