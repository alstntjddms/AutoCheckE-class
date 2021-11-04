from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from dotenv import load_dotenv
from datetime import datetime
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

 # 강의목록
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

def learn_class(ID, PW, WEEK, CLASS, VIDEO, PERFORMANCE, hlist, txt):

    txt.append("홈페이지 로그인 시도!")
    txt.append("")
    txt.append("============실행목록============")

    driver = webdriver.Chrome()

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

            QtSleep(runningtime / 100)

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



class MyApp(QWidget):

    def __init__(self):
        super().__init__()

        # 상단바 제거
        self.setWindowFlag(Qt.CustomizeWindowHint)

        # 창 전체
        self.setWindowTitle('Icon')
        self.setWindowIcon(QIcon('hansung.ico'))
        self.setWindowTitle('출석체크 플레이어')
        self.setFixedSize(720, 420)
        self.center()

        # UI불러오기
        self.initUI()

    def initUI(self):

        # 버튼
        btn1 = QPushButton('로그인', self)
        btn1.move(560, 285)
        btn1.resize(btn1.sizeHint())
        btn1.clicked.connect(self.login_button_event)

        btn2 = QPushButton('실행', self)
        btn2.move(635, 285)
        btn2.resize(btn2.sizeHint())
        btn2.clicked.connect(self.play_button_event)


        btn3 = QPushButton('종료', self)
        btn3.move(560, 310)
        btn3.resize(150, 25)
        btn3.clicked.connect(QCoreApplication.instance().quit)

        # 로그인
        self.ID = QLineEdit(self)
        self.ID.setValidator(QIntValidator())
        self.ID.setText("1694072")

        self.ID.move(560, 60)

        self.PW = QLineEdit(self)
        self.PW.move(560, 100)
        self.PW.setText("Alstn3599@@")

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

        # 라벨
        self.label2 = QLabel(self)
        self.label2.move(600, 10)
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
        self.label9.move(5, 385)
        self.label9.setText("텍스트 테스트중 테스트 테스트")
        self.label9.setFont(QFont("D2Coding", 10, QFont.Medium))

        self.label10 = QLabel(self)
        self.label10.move(5, 400)
        self.label10.setText("텍스트 테스트중 테스트테테테테테테ㅔ테테테테ㅔ테테테테")
        self.label10.setFont(QFont("D2Coding", 10, QFont.Medium))

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

    # 텍스트콘솔추가
    #def textedit(self, consol):
    #    self.text.append(consol)

    # 로그인버튼이벤트리스너
    def login_button_event(self):
        ID, PW = self.ID.text(), self.PW.text()
        self.txt.append(ID + "학번으로 로그인 시도")

        self.clist, self.hlist = prof_class_list(ID, PW)

        if len(self.clist) <1:
            self.txt.append(ID + "학번으로 로그인 실패! 아이디를 확인하세요")
            QMessageBox.about(self, "로그인", "로그인 실패!\n아이디를 확인하세요.")
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
        ID, PW, WEEK, CLASS, VIDEO, PERFORMANCE, hlist, txt = self.ID.text(), self.PW.text(), self.WEEK.text(), int(self.CLASS.text()), int(self.VIDEO.text()), float(self.PERFORMANCE.text()), self.hlist, self.txt
        learn_class( ID, PW, WEEK, CLASS, VIDEO, PERFORMANCE, hlist, txt)

    # 콘솔창 입력
    def append_text(self):
        self.txt.append("")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())