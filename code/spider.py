#author:timevshow
import requests
from bs4 import BeautifulSoup 
import re
import time
import random
import os
flag = 1 
reviewNum = 0
likeNum = 0
shareNum = 0
src = ''#存取文件的路径
headers = {
    'User-agent' : '',
    'Host' : 'weibo.cn',
    'Accept' : 'application/json, text/plain, */*',
    'Accept-Language' : 'zh-CN,zh;q=0.9',
    'Accept-Encoding' : 'gzip, deflate, br',
    'Cookie':'',
    'DNT' : '1',
    'Connection' : 'keep-alive'
}#请求头的书写，包括User-agent,Cookie等,请更换为自己对应的User-agent，以及cookie



def get_one_page(url):#请求函数：获取某一网页上的所有内容
    response = requests.get(url,headers = headers,verify=False)#利用requests.get命令获取网页html
    if response.status_code == 200:#状态为200即为爬取成功
        return response.text#返回值为html文档，传入到解析函数当中
    return None

def getNewsPicture(id):#获取新闻中的所有图片，并存储到对应的年月文件中
    print("开始爬取文章图片")
    picture = requests.get("https://weibo.cn/mblog/picAll/"+id+"?rl=1",headers = headers)
    soup = BeautifulSoup(picture.text,'lxml')
    pictures = soup.select('img')
    if(pictures is not None):
        if not os.path.exists(src+str(id)):
            os.mkdir(src+str(id))
        filePath = src+str(id)+"/"
        for i in range(0,len(pictures)):
            response = requests.get(pictures[i].attrs['src'])
            if(response.status_code == 200):
                with open(filePath+str(i)+".jpg",'wb') as file:
                    file.write(response.content)
        print("爬取图片完毕")

def getPages(id):
    url = "https://weibo.cn/1618051664/"+id+"?page=1"#生成访问的对应url
    html = get_one_page(url)
    print('正在爬取第1页评论')
    parse_one_page(html,src+id+".txt")
    print("解析完毕")
    soup = BeautifulSoup(requests.get(url,headers = headers).text,'lxml')
    txt = soup.find(class_="pa")
    if(txt is None):
        return 0
    else:
        txt = txt.text.split()[-1:][0]
    pages = int(txt.split('/')[1][:-1])
    time.sleep(3)
    return pages
        

def parse_one_page(html,filePath):#解析html并存入到文档result.txt中
    file = open(filePath,'a+')
    soup = BeautifulSoup(html,'lxml')
    news = soup.find(id="M_")
    flag = 0
    if(news is not None):
        newC = news.text.split()
        links = news.select('a')
        content = ''
        for i in range(1,len(newC) - 6):
            content += newC[i]
        content = content[1:]
        file.write("news:\n"+content+"\n")
        if(links is not None):
            for eachone in links:
                if(re.match('.*/video/.*',eachone.attrs['href'])):
                    print(eachone.attrs['href'])
                    file.write("video:\n"+eachone.attrs['href']+"\n")
                    break
        file.write("data:\n"+"shareNum:"+str(shareNum)+"reviewNum:"+str(reviewNum)+"likeNum:"+str(likeNum)+"\n")
        flag = 1
    if(flag == 1):
        file.write("review:\n")
    review = soup.find_all(class_="ctt")[flag:]
    for eachone in review:
        file.write(eachone.text+"\n")

if __name__ == '__main__':
    flag = 0
    codedir = 'EventIDNums'
    blogdir = 'blogs/'
    if not os.path.exists("blogs/pictures"):
        os.mkdir("blogs/pictures")
    year = os.listdir(codedir)
    for eachy in year:
        list = os.listdir(codedir+"/"+eachy)
        for eachym in list:
            m = int(eachym.replace('code.txt',''))
            src = blogdir + str(eachy)+"/"+str(m)
            if not os.path.exists(src):
                os.mkdir(src)
            src = src + "/"
            print(src)
            if(m == 5 or m == 6 or m == 7 or m == 9 or m == 12):
                continue
            lines = open(codedir+"/"+eachy+"/"+eachym, 'r').readlines()
            for j in range(0,len(lines)):
                print("第"+str(m)+"月"+str(j)+">>>>>>>>"+str(len(lines)))
                index, id, reviewNum ,shareNum ,likeNum= lines[j].split()
                if(os.path.exists(src+id+".txt")):
                    print("已存在")
                    continue
                content = ''
                getNewsPicture(id)
                pages = min(15,getPages(id))#获取评论的页数,控制最多只读取到15页
                flag = 1
                for i in range(2,pages + 1):  # 页数
                    url = "https://weibo.cn/1618051664/"+id+"?page="+str(i)
                    html = get_one_page(url)
                    print('正在爬取第 %d 页评论' % (i))
                    parse_one_page(html,src+id+".txt")
                    print("解析完毕")
                    time.sleep(3)
