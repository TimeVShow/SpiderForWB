#author:timevshow
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import re
import os
year = '2020'#此处修改年份
loginUrl = 'https://passport.weibo.cn/sigin/login'
baseUrl = 'https://www.weibo.com/breakingnews?is_all=1&stat_date='+year
browser = webdriver.Chrome()
browser.implicitly_wait(5)
wait = WebDriverWait(browser,10)
scriptT = ""
scriptF = "window.scrollTo(document.body.scrollHeight,0)"
filePath = "EventIDNums/"+year
breakpointfile = "breakpoint.txt"#判定断点文件
breakmonth = 0
breakpages = 0

def windowScroll():#滚动页面
    browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(6)
    browser.execute_script("window.scrollTo(document.body.scrollHeight,2*document.body.scrollHeight)")
    time.sleep(6)
    browser.execute_script("window.scrollTo(document.body.scrollHeight,0)")
    time.sleep(6)

def login():#进行登录,使用手机验证码登录，每账号每天可验证3次，24小时后验证次数重置
    browser.get(loginUrl)
    browser.find_element_by_id('loginName').send_keys('')#替换为自己的微博账号
    browser.find_element_by_id('loginPassword').send_keys('')#替换为自己的密码
    time.sleep(1)
    browser.find_element_by_id('loginAction').click()
    time.sleep(60)    
    print("login successfully!!!")

def getIDNums():
    for month in range(breakmonth,0,-1):#按月份
        num = 1
        if(month < breakmonth):
            targetpages = 1  
        else:
            targetpages = breakpages
        #创建Url
        if(month >= 10):
            Url = baseUrl + str(month)
        else:
            Url = baseUrl + "0" + str(month)
        for page in range(targetpages,41):
            url = Url + "&page=" + str(page)
            browser.get(url)
            time.sleep(5)
            print("页面加载完毕,开始滚动页面")
            windowScroll()
            print("开始爬取第"+str(page)+"页")
            #存断点文件
            with open(breakpointfile,'w') as bf:
                bf.write(str(month)+" "+str(page))
            articles = browser.find_elements_by_class_name('WB_feed_handle')
            #开始读取页面
            for article in articles:
                details = article.find_elements_by_css_selector('.pos span')
                shareNum = details[2].text[1:]
                likeNum = details[6].text[1:]
                review = details[4]
                reviewNum = details[4].text[1:]
                review.click()
                time.sleep(1)
                hrefs = browser.find_elements_by_css_selector('.list_ul a')
                if(len(hrefs) == 0):
                    continue
                href = hrefs[len(hrefs) - 1].get_attribute("href")
                if(href is None):
                    continue
                code = re.search("\d/\w.*\?",href)
                if(code is None):
                    continue
                #获取本篇微博代码
                code = code.group(0)[2:-1]
                review.click()
                #写文件
                with open(filePath+"/"+str(month)+"code.txt",'a') as file:
                    file.write(str(num)+" "+str(code)+" "+str(reviewNum)+" "+str(shareNum)+" "+str(likeNum)+"\n")
                num = num + 1

def getbreakpoint():#得到断点信息
    if(os.path.exists(breakpointfile)):
        with open(breakpointfile,'r') as bf:
            data = bf.readline()
            breakmonth,breakpages = data.split()
            breakmonth = int(breakmonth)
            breakpages = int(breakpages)
            if(breakpages < 40):
                breakpages = breakpages + 1
            else:
                breakmonth = breakmonth - 1       
                breakpages = 1
    else:
        breakmonth = 12
        breakpages = 1
    return breakmonth,breakpages

if __name__ == "__main__":
    if(not os.path.exists(filePath)):
        os.mkdir(filePath)
    breakmonth,breakpages = getbreakpoint()
    login()#必须登录后才能按月份查询
    getIDNums()#进行对数据的处理





