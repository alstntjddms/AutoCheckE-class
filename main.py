from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium.webdriver.common.alert import Alert
from datetime import datetime

# 문자열시간 초로바꾸기
def time_to_sec_hour(t):
   h, m, s= map(int, t.split(':'))
   return h * 3600 + m * 60 + s

def time_to_sec_min(t):
   m, s= map(int, t.split(':'))
   return  m * 60 + s

# 로그인
print("==========================================주의사항=============================================")
print("==============본 프로그램은 한성대학교 e-class 첫1회 출석인증 프로그램입니다.==================")
print("=배속이 걸려 있지 않고 selenium을 기반으로 구현해 실제 사람이 듣는 것과 서버기록에 동일합니다.=")
print("====컴퓨터 종료시 프로그램이 중단됩니다. 실제로 사람이 직접 x1배속으로 켜놓는것과 같습니다.====")
print("=========Chrome의 버전과 chromedriver의 버젼이 같아야합니다.(94.0.xxx.xx)입니다. ==============")
print("====================본 프로그램은 서버에 어떠한 정보도 저장하지 않습니다. =====================")
ID = input("아이디를 입력하세요. : ")
PW = input("비밀번호를 입력하세요. : ")
WEEK = input("이번주차를 입력하세요. 틀리면 로그인 불가: ")
print("===============================================================================================")
print("==============이번주 강의를 처음들으시는분은 아래 두개 설정을 0으로 해주세요.==================")
print("=============강의순번은 e-class맨위에있는 강의가 0번으로 내려갈수록 1씩 커집니다. =============")
print("==============동영상도  강좌페이지 맨위에서부터 0번으로 내려갈수록 1씩커집니다.================")
print("==========온라인 출석부에서 확인하셔서 끊기신부분부터 보시면 됩니다.[0부터 시작입니다.]========")
print("===============================================================================================")
CLASS = int(input("시작하고싶은 강의순번을 입력하세요 : "))
VIDEO = int(input("시작하고싶은 동영상 입력하세요 : "))
PERFOMANCE = float(input("컴퓨터가 좋지 안다면 늘리세요. 대기시간설정[빠름1, 기본1.5, 느림3] : "))

if PERFOMANCE < 1:
    print("성능설정은 최소1입니다.")
    exit()

KEY = input("비밀번호를 입력하세요 : ")

ANSWER = ('ha16abc')

if datetime.today().year != 2021:
    print("연도가 다릅니다.")
    exit()

if KEY in ANSWER:
    pass
else:
    print("비밀번호가 틀립니다.")
    exit()

print("=========================================로그인 성공===========================================")

# 세션설정
load_dotenv()
session = requests.session()

# login session data
login_info = {
    "username": ID,
    "password": PW
}

headers = {
    "User-Agent" : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.232 Whale/2.10.124.26 Safari/537.36',
    "Referer" : 'https://learn.hansung.ac.kr/login.php'
          }

url_login = "https://learn.hansung.ac.kr/login/index.php"
res = session.post(url_login, data = login_info, headers = headers)
if res.status_code != 200:
        raise Exception("Login failed.")

soup = BeautifulSoup(res.text, 'html.parser')
hreflist = soup.select('.course_label_re_02>div>a')
proflist = soup.select('.prof')

plist = list()
clist = list()

#강의주소
for a in hreflist:
    clist.append(a.attrs['href'])
print("강의주소를 불러왔습니다.")

# 교수리스트
for x in proflist:
    plist.append(x.string)
#print("교수리스트")


######driver######
driver = webdriver.Chrome()
# Alert 잡기

driver.get("http://learn.hansung.ac.kr/")
sleep(1 * PERFOMANCE)
id = driver.find_element_by_name("username")
pw = driver.find_element_by_name("password")

id.send_keys(ID)
pw.send_keys(PW)
pw.send_keys(Keys.RETURN)

clistnum = 0

# 주차 설정
section = WEEK

for classes in clist:
    if CLASS > 0:
        CLASS -= 1
        clistnum += 1
        continue
    #수업별로들어가기
    driver.get(clist[clistnum])
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    obj = soup.find('li', id = 'section-' + section)
    #print(obj)

    # 동영상 리스트 정리
    olist = list()
    for item in obj.find_all('a', {'href': True}):
         if (item['href'].find('vod') > 0):
             slicenum = item['href'].find('=')
             tmpitem = item['href'][slicenum+1 : ]
             olist.append(tmpitem)
    #print(olist)

    #동영상 시작
    numclass = 0
    chkclass = True
    for prelist in olist:
        if VIDEO > 0:
            VIDEO -= 1
            numclass += 1
            continue
        if len(olist) < numclass+1:
            break

        # 강의영상 플레이
        driver.get('http://learn.hansung.ac.kr/mod/vod/viewer.php?id='+olist[numclass])
        sleep(1 * PERFOMANCE)
        try:
            Alert(driver).accept()
            #print("재생한 기록있음1")
            chkclass = False
        except:
            print("강의 실행")

        if chkclass == True:
            chkclass = True
            driver.find_elements_by_id("vod_player")[0].click()
        else:
            chkclass = True

        #재생시간
        sleep(3)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        runningtime = soup.find(class_='jw-text jw-reset jw-text-duration').get_text()
        if len(runningtime) > 6:
            runningtime = time_to_sec_hour(runningtime)
        else:
            runningtime = time_to_sec_min(runningtime)
        print(runningtime)
        sleep(runningtime*1.03)
        numclass += 1
        driver.back()
        sleep(1 * PERFOMANCE)
        try:
            Alert(driver).accept()
            sleep(1 * PERFOMANCE)
        except:
            sleep(1 * PERFOMANCE)

    clistnum += 1

