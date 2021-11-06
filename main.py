from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from dotenv import load_dotenv
import sys
import requests
from selenium.webdriver.common.alert import Alert
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

 # 문자열시간 초로바꾸기
def time_to_sec_hour(t):
   h, m, s= map(int, t.split(':'))
   return h * 3600 + m * 60 + s

def time_to_sec_min(t):
   m, s= map(int, t.split(':'))
   return  m * 60 + s

 # PyQt sleep
def QtSleep(t):
    loop = QEventLoop()
    QTimer.singleShot(1000*t, loop.quit)  # msec
    loop.exec_()

 # bs4 강의목록
def prof_class_list(ID, PW):
    # 세션설정
    load_dotenv()
    session = requests.session()

    # login session data
    login_info = {
        "username": ID,
        "password": PW
    }

    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.232 Whale/2.10.124.26 Safari/537.36',
        "Referer": 'https://learn.hansung.ac.kr/login.php'
    }

    url_login = "https://learn.hansung.ac.kr/login/index.php"
    res = session.post(url_login, data=login_info, headers=headers)
    if res.status_code != 200:
        raise Exception("Login failed.")

    soup = BeautifulSoup(res.text, 'html.parser')

    hreflist = soup.select(
        '.course_label_re_02>div>a'
    )

    classlist = soup.select(
        '.course_label_re_02>.course_box>.course_link>.course-name>.course-title>h3'
    )

    clist = list()
    hlist = list()

    # # 수업 리스트
    for c in classlist:
        clist.append(c.text)

    # 강의주소
    for h in hreflist:
        hlist.append(h.attrs['href'])

    return clist, hlist

 # seleminum 강의 재생
def learn_class(ID, PW, WEEK, CLASS, VIDEO, PERFORMANCE, hlist, txt, mute, browser):

    txt.append("홈페이지 로그인 시도!")
    txt.append("")
    txt.append("============실행목록============")

    options = webdriver.ChromeOptions()

    print(mute, browser)
    # 체크박스 옵션설정
    if mute == True:
        options.add_argument('--mute-audio')
    if browser == True:
        options.add_argument('incognito')

    driver = webdriver.Chrome(chrome_options=options)

    print("xx3")

    driver.get("http://learn.hansung.ac.kr/")

    QtSleep(1 * PERFORMANCE)

    id = driver.find_element(By.ID, "input-username")
    pw = driver.find_element(By.ID, "input-password")

    # 로그인
    id.send_keys(ID)
    pw.send_keys(PW)
    pw.send_keys(Keys.RETURN)

    hlistnum = 0

    for classes in hlist:

        # 설정한 시작강의 맞추기
        if CLASS > 0:
            CLASS -= 1
            hlistnum += 1
            continue

        #수업별로들어가기

        driver.get(hlist[hlistnum])
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        obj = soup.find('li', id = 'section-' + WEEK)

        # 동영상 리스트 정리
        olist = list()
        for item in obj.find_all('a', {'href': True}):
             if (item['href'].find('vod') > 0):
                 slicenum = item['href'].find('=')
                 tmpitem = item['href'][slicenum+1 : ]
                 olist.append(tmpitem)

        #동영상 시작
        chkclass = True

        vlistnum = 0
        for tmplist in olist:

            # 설정한 시작동영상 맞추기
            if VIDEO > 0:
                VIDEO -= 1
                vlistnum += 1
                continue

            if len(olist) < vlistnum+1:
                break

            # 강의영상 플레이
            driver.get('http://learn.hansung.ac.kr/mod/vod/viewer.php?id='+olist[vlistnum])
            QtSleep(1 * PERFORMANCE)

            try:
                Alert(driver).accept()
                chkclass = False
            except:
                pass

            if chkclass == True:
                chkclass = True
                driver.find_element(By.ID, "vod_player").click()
            else:
                chkclass = True

            #재생시간
            QtSleep(3)
            html = driver.page_source

            soup = BeautifulSoup(html, 'html.parser')
            runningtime = soup.find(class_='jw-text jw-reset jw-text-duration').get_text()

            if len(runningtime) > 6:
                runningtime = time_to_sec_hour(runningtime)
            else:
                runningtime = time_to_sec_min(runningtime)

            txt.append("{}번 강의, {}번 동영상 재생중". format(hlistnum, vlistnum))
            txt.append("{}초 후 다음 강의 실행". format(runningtime))

            QtSleep(runningtime / 1000)

            vlistnum += 1
            driver.back()

            sleep(1 * PERFORMANCE)
            try:
                Alert(driver).accept()
                QtSleep(1 * PERFORMANCE)
            except:
                QtSleep(1 * PERFORMANCE)

        hlistnum += 1

    txt.append("================================")
    txt.append("")
    txt.append("출석체크 완료")
    driver.quit()

# 서버에서 버전 로드
def load_version():

    url = 'https://medium.com/@1694072/%ED%85%8C%EC%8A%A4%ED%8A%B8-153168ef754f'
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    oldv = soup.find(id="6d67" ).text
    newv = soup.find(id="3e57" ).text

    if float(oldv) < float(newv):
        return True
    else:
        return False

# 서버에서 공지사항 로드
def load_text():

    url = 'https://medium.com/@1694072/%ED%85%8C%EC%8A%A4%ED%8A%B8-153168ef754f'
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    t1 = soup.find(id="94cf" ).text
    t2 = soup.find(id="86a1" ).text

    return t1, t2

# 서버에서 KEY로드
def load_key():

    url = 'https://medium.com/@1694072/%ED%85%8C%EC%8A%A4%ED%8A%B8-153168ef754f'
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    key = soup.find(id="82cb" ).text

    return key

class MyApp(QWidget):

    # 생성자
    def __init__(self):
        super().__init__()

        # 상단바 제거
        self.setWindowFlag(Qt.CustomizeWindowHint)

        # 창 전체
        self.setWindowTitle('Icon')
        self.setWindowIcon(QIcon('hansung.ico'))
        self.setWindowTitle('출석체크 플레이어 2.0')
        self.setFixedSize(720, 420)
        self.center()

        # UI불러오기
        self.initUI()

        if load_version() == True:
            QMessageBox.about(self, "VERSION 2.0", "새로운 버전 확인!\n새로운 버전을 받아주세요")

    # UI
    def initUI(self):

        # 버튼
        btn1 = QPushButton('로그인', self)
        btn1.move(560, 355)
        btn1.resize(btn1.sizeHint())
        btn1.clicked.connect(self.login_button_event)

        btn2 = QPushButton('실행', self)
        btn2.move(635, 355)
        btn2.resize(btn2.sizeHint())
        btn2.clicked.connect(self.play_button_event)

        btn3 = QPushButton('종료', self)
        btn3.move(560, 380)
        btn3.resize(150, 25)
        btn3.clicked.connect(QCoreApplication.instance().quit)

        # 로그인
        self.ID = QLineEdit(self)
        self.ID.setValidator(QIntValidator())

        self.ID.move(560, 60)

        self.PW = QLineEdit(self)
        self.PW.move(560, 100)

        # 비밀번호는 안보이게
        self.PW.setEchoMode(QLineEdit.Password)

        self.WEEK = QLineEdit(self)
        self.WEEK.setValidator(QIntValidator())
        self.WEEK.move(560, 140)

        self.CLASS = QLineEdit(self)
        self.CLASS.setValidator(QIntValidator())
        self.CLASS.setText("0")
        self.CLASS.move(560, 180)

        self.VIDEO = QLineEdit(self)
        self.VIDEO.setValidator(QIntValidator())
        self.VIDEO.setText("0")
        self.VIDEO.move(560, 220)

        self.PERFORMANCE = QLineEdit(self)
        self.PERFORMANCE.setValidator(QIntValidator())
        self.PERFORMANCE.setText("1.5")
        self.PERFORMANCE.move(560, 260)

        self.KEY = QLineEdit(self)
        self.KEY.move(560, 300)

        # 라벨
        self.label2 = QLabel(self)
        self.label2.move(600, 15)
        self.label2.setText("로그인")
        self.label2.setFont(QFont("D2Coding", 18, QFont.Black))

        self.label3 = QLabel(self)
        self.label3.move(560, 45)
        self.label3.setText("학번")
        self.label3.setFont(QFont("D2Coding", 10, QFont.Black))

        self.label4 = QLabel(self)
        self.label4.move(560, 85)
        self.label4.setText("비밀번호")
        self.label4.setFont(QFont("D2Coding", 10, QFont.Black))

        self.label5 = QLabel(self)
        self.label5.move(560, 125)
        self.label5.setText("이번주차")
        self.label5.setFont(QFont("D2Coding", 10, QFont.Black))

        self.label6 = QLabel(self)
        self.label6.move(560, 165)
        self.label6.setText("강의순번")
        self.label6.setFont(QFont("D2Coding", 10, QFont.Black))

        self.label7 = QLabel(self)
        self.label7.move(560, 205)
        self.label7.setText("강의 내 순번")
        self.label7.setFont(QFont("D2Coding", 10, QFont.Black))

        self.label8 = QLabel(self)
        self.label8.move(560, 245)
        self.label8.setText("대기시간설정(1~3)")
        self.label8.setFont(QFont("D2Coding", 10, QFont.Black))

        self.label9 = QLabel(self)
        self.label9.move(560, 285)
        self.label9.setText("이번주 KEY 입력")
        self.label9.setFont(QFont("D2Coding", 10, QFont.Black))

        # 하단 텍스트
        t1, t2 = load_text()
        self.label9 = QLabel(self)
        self.label9.move(5, 385)
        self.label9.setText(t1)
        self.label9.setFont(QFont("D2Coding", 10, QFont.Medium))

        self.label10 = QLabel(self)
        self.label10.move(5, 400)
        self.label10.setText(t2)
        self.label10.setFont(QFont("D2Coding", 10, QFont.Medium))

        # 체크박스
        self.cb = QCheckBox('음소거', self)
        self.cb.move(565, 330)
        self.cb.toggle()
        self.cb.stateChanged.connect(self.changeTitle)

        self.cb1 = QCheckBox('시크릿 모드', self)
        self.cb1.move(625, 330)
        self.cb1.toggle()
        self.cb1.stateChanged.connect(self.changeTitle)

        # 콘솔창 출력
        self.txt = QTextBrowser(self)
        self.txt.resize(550, 380)
        self.show()

    # 화면 중앙으로 키기
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # 로그인버튼이벤트리스너
    def login_button_event(self):
        KEY = self.KEY.text()
        ID, PW = self.ID.text(), self.PW.text()
        self.txt.append(ID + "학번으로 로그인 시도...")

        self.clist, self.hlist = prof_class_list(ID, PW)

        # 아이디나 비밀번호 입력확인
        if len(ID) < 1 or len(PW) < 1:
            self.txt.append(ID + "학번으로 로그인 실패! 아이디를 확인하세요")
            QMessageBox.about(self.ID, "로그인", "로그인 실패!\n아이디와 비밀번호를 입력하세요.")
        # 아이디 체크
        elif len(self.clist) < 1:
            self.txt.append(ID + "학번으로 로그인 실패! 아이디를 확인하세요")
            QMessageBox.about(self.ID, "로그인", "로그인 실패!\n아이디를 확인하세요.")

        # KEY 체크
        elif KEY != load_key():
            QMessageBox.about(self.ID, "KEY", "로그인 실패!\n이번주 KEY를 확인하세요.")
        # 로그인 성공
        else:
            # 로그인 성공시 강의목록띄우기
            self.txt.append("")
            self.txt.append("============강의목록============")
            for i in range(len(self.clist)):
                self.txt.append(self.clist[i])
            self.txt.append("================================")
            self.txt.append("")
            QMessageBox.about(self, "로그인", "로그인 성공!")
    # 실행버튼이벤트리스너
    def play_button_event(self):
        learn_class(self.ID.text(), self.PW.text(), self.WEEK.text(), int(self.CLASS.text()), int(self.VIDEO.text()), float(self.PERFORMANCE.text()), self.hlist, self.txt, self.cb.isChecked(), self.cb1.isChecked())

    # 체크박스 이벤트 리스너
    def changeTitle(self, state):
        if state == Qt.Checked:
            return True
        else:
            return False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())