from socket import *
from threading import *
import time
import pymysql
import struct
import datetime
import os
import sys
import json
connection_socket_list = {}

'''
 0  메세지인지(m),             파일이면(f)     닉네임(n)   친구(u)                   상태(s)
 1  1:1메세지 : p, 1:n메세지:n              중복체크(y/n)   요청(r) 수락거절(y/n)    온라인상태(o/f)
 2  파일이름전송:s 파일 수락:a 파일 거절:r 데이터:d 데이터전송끝:e 
 3
 
 4   크기 고정
 5
 6
 7
'''
'''
U 친구
-R 요청                                   -S 검색                           -A 친구 신청된거 주세요         -I 알림왔어요
-L 요청 리스트  -Y 수락  -N 거절           -L 리스트  -R 신청                -S 주고 -R 받기                 -R 친구 신청 
-S 주고 -R 받기


DataBase
We
 -F 친구
 -P 신청 
 -B 차단
'''
HEADER_SIZE = 8

fmt = '=4si'
fmt_size = struct.calcsize(fmt)


class ServerRecv(Thread):
    global connection_socket_list
    def __init__(self, sock, addr):
        super().__init__()
        self.sock = sock
        self.addr = addr
        self.DBconnect = pymysql.connect(
            host = 'localhost', user = 'babo', password = 'sangmin', db = 'GAME', charset = 'utf8')
        self.DBcursor = self.DBconnect.cursor()
        self.login = 0
        self.ID = ""
        '''
        self.DBcursor.execute(
            "SELECT * FROM sqlite_master WHERE type= 'table';")
        TableName = self.DBcursor.fetchall()

        if 'Friends' not in TableName or 'Users' not in TableName:
            self.DBcursor.execute("CREATE TABLE IF NOT EXISTS users (id primary key, \
                    password TEXT NOT NULL, \
                    name TEXT NOT NULL, \
                    socket TEXT);")
            self.DBconnect.commit()
            self.DBcursor.execute("CREATE TABLE IF NOT EXISTS friends (id TEXT NOT NULL, \
                        You TEXT NOT NULL, \
                        We_Friend TEXT NOT NULL);")
            self.DBconnect.commit()
            self.DBcursor.execute("CREATE TABLE IF NOT EXISTS chatting (id TEXT NOT NULL, \
                        You TEXT NOT NULL, \
                        chat TEXT NOT NULL, \
                        Date int, \
                        Time int);")
            self.DBconnect.commit()
        '''
            
        self.DBcursor.execute("SELECT * FROM Users")
        A = self.DBcursor.fetchall()
        print(A)

    def run(self):
        while True:
            try:
                Date = datetime.datetime.now()
                self.Date = Date.year * 10000 + Date.month * 100 + Date.day
                self.Time = Date.hour * 100 + Date.minute
                recv_data_header = self.sock.recv(HEADER_SIZE)
                print(recv_data_header)
                header = struct.unpack(fmt, recv_data_header)
                recvData = self.sock.recv(header[1]).decode()
                print(header)
                print(recvData)

                if header[0][0] == 109:
                    if header[0][1] == 112:
                        print('개인용 메세지', recvData)
                        Chatting_Data = json.loads(recvData)
                        print(Chatting_Data)
                        Friend_send = Chatting_Data[0]
                        Chatting = Chatting_Data[1]
                        
                        sql = f"SELECT sock FROM Users WHERE name = '{Friend_send}';"
                        self.DBcursor.execute(sql)
                        sock = self.DBcursor.fetchall()
                        sock = sock[0][0]
                        print(sock)
                        sock = 1
                        if sock == 1:
                            print("진입중")
                            send_sock = connection_socket_list[Friend_send]
                            print(send_sock)
                            send_data = struct.pack(fmt, b'mp00', len(Chatting.encode('utf-8')))
                            send_sock.send(send_data + Chatting.encode('utf-8'))
                            '''
                            #온라인
                            sql = f"SELECT idx FROM Users WHERE name = '{Friend_send}';"
                            self.DBcursor.execute(sql)
                            idx = self.DBcursor.fetchall()
                            friend_idx = idx[0][0]
                            sql = f"SELECT ip, port FROM SOCK WHERE idx = '{friend_idx}';"
                            self.DBcursor.execute(sql)
                            friend_ip = self.DBcursor.fetchall()
                            print(friend_ip[0][0])
                            print(friend_ip[0][1])
                            SendSock = socket(AF_INET,SOCK_STREAM)
                            SendSock.connect((friend_ip[0][0], friend_ip[0][1]))
                            print(SendSock)
                            send_data.struct.pack(fmt, b'SF00',len(Chatting.encode('utf-8')))
                            SendSock.send(send_data + Chatting.encode('utf-8'))
                            SendSock.close()
                            '''
                        else:
                            #오프라인
                            pass
                        #위에 idx 정보와 sock 테이블 정보를 합쳐서 소켓 생성해서 전송
                        '''
                        you_no = self.DBcursor.execute(f"SELECT sock FROM Users WHERE name = '{you_name}'")
                        # you_sock = self.DBcursor.execute(f"SELECT *"

                        self.DBcursor.execute(f"INSERT INTO Chatting (idx, Sender , Recipient, Contents,  Time) VALUES (?, ?, ?, ?, ?);", (
                           NULL ,my_id[0], you_sock[0], recvData[1], self.Time))
                        self.DBconnect.commit()
                        if my_sock[3] != '':
                            send_header = struct.pack(fmt, b'SF00', len(
                                my_id[2]+":"+recvData[1].encode('utf-8')))
                            you_sock[4].send(
                                send_header + (my_id[2]+":"+recvData[1]).encode('utf-8'))
                        '''
                    elif header[0][1] == 110:
                        print('1:n메세지 수신', recvData.decode())

                elif header[0][0] == 102:
                    pass

                elif header[0][0] == 85:
                    '''
                    if header[0][1] == 76:
                        
                        self.DBcursor.execute("SELECT YOUR_ID FROM Friends WHERE MY_ID = '{self.ID}' AND state = 'F';")
                        if not self.DBcursor.fetchall():
                            pass
                        else:
                            My_Friends = self.DBcursor.fetchall()
                            send_header = struct.pack(fmt,b'UU00',len(My_Friends.encode('utf-8')))
                            self.sock.send(send_header + My_Friends.encode('utf-8'))
                        # 친구 리스트 주세요
                        self.DBcursor.execute(
                            "SELECT identity FROM Users WHERE sock = {self.sock.fileno};")
                        # literal_eval 문자열을 리스트또는 튜플로 변환
                        Imsi_id = self.DBcursor.fetchall()
                        self.DBcursor.execute(
                            "SELECT YOUR_ID FROM Friends WHERE MY_ID '%s' AND state = '%s';" % (Imsi_id, 'F'))
                        My_Friends = self.DBcursor.fetchall()
                        send_header = struct.pack(
                            fmt, b'UU00', len(My_Friends.encode('utf-8')))
                        self.sock.send(
                            send_header + My_Friends.encode('utf-8'))
                        '''
                    if header[0][1] == 76:
                        if header[0][2] == 82:
                            # 친구 요청 받은 리스트 주세요
                            sql = f"SELECT MY_ID FROM Friends WHERE YOUR_ID = '{self.ID}' AND state = 'P';"
                            self.DBcursor.execute(sql)
                            first = self.DBcursor.fetchall()
                            friend_list = ''
                            if len(first) != 0:
                                for friend in first[0]:
                                    if friend_list != '':
                                        friend_list = friend[0]
                                    else:
                                        friend_list = friend_list + ',' + friend[0]
                            sql = f"SELECT YOUR_ID FROM Friends WHERE MY_ID = '{self.ID}' AND state = 'P';"
                            self.DBcursor.execute(sql)
                            second = self.DBcursor.fetchall()
                            if len(second) != 0:
                                for i in second[0]:
                                    for friend in i:
                                        if friend_list != '':
                                            friend_list = friend
                                        else:
                                            friend_list = friend_list + ',' + friend
                            print(friend_list)
                            send_header = struct.pack(fmt, b'URL0', len((friend_list).encode('utf-8')))
                            self.sock.send(send_header + (friend_list).encode('utf-8'))
                        elif header[0][2] == 89:
                            # 친구 신청 수락할래요
                            sql = f"SELECT identity FROM Users WHERE name = '{recvData}';"
                            self.DBcursor.execute(sql)
                            You_id = self.DBcursor.fetchall()
                            You_id = You_id[0][0]
                            sql = f"SELECT idx FROM Friends WHERE MY_ID = '{self.ID}' AND YOUR_ID = '{You_id}';"
                            self.DBcursor.execute(sql)
                            F = self.DBcursor.fetchall()
                            print(type(F))
                            if F == ():
                                sql = f"SELECT idx FROM Friends WHERE MY_ID = '{You_id}' AND YOUR_ID = '{self.ID}';"
                                self.DBcursor.execute(sql)
                                F = self.DBcursor.fetchall()
                            print(F)

                            F = F[0][0]
                            sql = f"UPDATE Friends SET state = 'Y' WHERE idx = '{F}';"
                            self.DBcursor.execute(sql)
                            self.DBconnect.commit()
                        elif header[0][2] == 78:
                            # 친구 신청 거절할래요
                            
                            self.DBcursor.execute("SELECT identity FROM Users WHERE name = '{recvData}';")
                            You_id = self.DBcursor.fetchall()

                            self.DBcursor.execute("SELECT idx FROM Friends WHERE MY_ID = '{self.ID}' AND YOUR_ID = '{You_id}';")
                            Friend = self.DBcursor.fetchall()
                            if Friend == '':
                                self.DBcursor.execute("SELECT idx FROM Friends WHERE MY_ID = '{You_id}' AND YOUR_ID = '{self.ID}';")
                                Friend = self.DBcursor.fetchall()

                            self.DBcursor.execute("UPDATE Friends SET state = 'N' WHERE idx = '{Friend}';")
                            self.DBconnect.commit()
                            
                    elif header[0][1] == 85:
                        if header[0][2] == 85:
                            print("진업")
                            # 검색 리스트 주세요
                            print(recvData)
                            if recvData != '':
                                print("1차 진입")
                                sql = f"SELECT name FROM Users WHERE name = '{recvData}'"
                                self.DBcursor.execute(sql)
                                Imsi_name = self.DBcursor.fetchall()
                            else:
                                self.DBcursor.execute(
                                    "SELECT name FROM Users LIMIT 25;")
                                Imsi_name = self.DBcursor.fetchall()
                            print(Imsi_name)
                            #Imsi_name = json.dumps(Imsi_name)
                            b = ''
                            for i in Imsi_name[0]:
                                if b == '':
                                    b = i
                                else:
                                    b = b+','+i

                            #print(len(Imsi_name.encode('utf-8')))
                            #send_header = struct.pack(fmt, b'URL0', len(Imsi_name.encode('utf-8')))
                            send_header = struct.pack(fmt, b'URL0', len(b.encode('utf-8')))
                            print(send_header)
                            print(send_header+b.encode('utf-8'))
                            print(len(send_header+b.encode('utf-8')))
                            self.sock.send(send_header+b.encode('utf-8'))
                            #send_header = struct.pack(fmt, b'URL0',0)
                            #self.sock.send(send_header)
                        elif header[0][2] == 82:
                            # 친구 신청 할래요
                            sql = f"SELECT identity FROM Users WHERE name = '{recvData}';"
                            self.DBcursor.execute(sql)
                            You_id = self.DBcursor.fetchall()
                            You_id = You_id[0][0]
                            print(You_id)
                            sql = f"INSERT INTO Friends (MY_ID, YOUR_ID , state) VALUES ('{self.ID}','{You_id}', 'P');"
                            self.DBcursor.execute(sql)
                            self.DBconnect.commit()
                    elif header[0][1] == 70:
                        if header[0][2] == 76:
                            #친구 목록
                            sql = f"SELECT YOUR_ID FROM Friends WHERE MY_ID = '{self.ID}' AND state = 'Y';"
                            self.DBcursor.execute(sql)
                            Friend = self.DBcursor.fetchall()
                            sql = f"SELECT MY_ID FROM Friends WHERE YOUR_ID = '{self.ID}' AND state = 'Y';"
                            self.DBcursor.execute(sql)
                            Friend_S = self.DBcursor.fetchall()
                            F_List = ''
                            for i in Friend:
                                if F_List == '':
                                    F_List = i[0]
                                else:
                                    F_List = F_List + ',' + i[0]
                            for i in Friend_S:
                                if F_List == '':
                                    F_List = i[0]
                                else:
                                    F_List = F_List + ',' + i[0]
                            print(F_List)
                            send_header = struct.pack(fmt, b'UAL0',len(F_List.encode('utf-8')))
                            self.sock.send(send_header + F_List.encode('utf-8'))

                            
                elif header[0][0] == 76:
                    if header[0][1] == 65:
                        print('진입완료')
                        self.ID, PW = recvData.split()
                        
                        self.DBcursor.execute("SELECT * FROM Users WHERE identity = '%s';" %self.ID)
                        DB_id = self.DBcursor.fetchone()
                        print(DB_id)
                        print(self.ID)
                        print(PW)
                        if not DB_id:
                            print('로그인 아이디 실패')
                            send_header = struct.pack(fmt, b'LF00', 0)
                            self.sock.send(send_header)
                        elif PW == DB_id[2]:
                            print('로그인 성공')
                            self.DBcursor.execute("SELECT * FROM Users WHERE identity = '%s';"%self.ID)
                            ABC = self.DBcursor.fetchall()

                            # laddr = str(self.sock.getsockname())
                            # raddr = str(self.sock.getpeername())
                            # print(type(laudr))
                            # print(type(raddr))
                            self.DBcursor.execute("SELECT idx FROM Users WHERE identity = '%s'" %self.ID)
                            idx = self.DBcursor.fetchall()
                            idx = idx[0][0]
                            print(idx)

                            sql = f"UPDATE Users SET sock = 1 WHERE identity = '{self.ID}';"
                            self.DBcursor.execute(sql)
                            self.DBconnect.commit()
                            print(self.sock.getsockname())
                            sql = f"UPDATE SOCK SET \
                                    fd = {self.sock.fileno()},\
                                    family = '{str(self.sock.family)}', \
                                    type = '{str(self.sock.type)}', \
                                    proto = {self.sock.proto}, \
                                    ip = '{self.sock.getpeername()[0]}', \
                                    port = {self.sock.getpeername()[1]} \
                                    WHERE idx = {idx};"
                            self.DBcursor.execute(sql)
                            self.DBconnect.commit()
                            ab = 'a'
                            sql = f"SELECT name FROM Users WHERE identity = '{self.ID}';"
                            self.DBcursor.execute(sql)
                            Nick = self.DBcursor.fetchall()
                            Nick = Nick[0][0]
                            connection_socket_list[Nick] = self.sock
                            connection_socket_list[self.sock] = Nick
                            send_header = struct.pack(fmt, b'LS00', 0)
                            self.sock.send(send_header)
                            abb = struct.pack(fmt,b'LS00',len(ab.encode('utf-8')))
                            #print(abb)
                            #print(len(abb + ab.encode('utf-8')))
                            #print(abb + ab.encode('utf-8'))
                            
                            self.login = 1
                            print(connection_socket_list)

                elif header[0][0] == 65:
                    if header[0][1] == 85:
                        print('받기 완료')
                    # 여기서 회원가입 아이디 비번 연결 성공 체크
                        ID, PW, NAME = recvData.split()
                        self.DBcursor.execute(
                            "SELECT identity FROM Users WHERE identity = '{ID}';")
                        print(ID)
                        print(PW)
                        print(NAME)
                        if not self.DBcursor.fetchall():
                            print('1차 통과')
                            self.DBcursor.execute("SELECT name FROM Users WHERE name = '%s';" %NAME)
                            if not self.DBcursor.fetchall():
                                print("회원가입 성공")
                                sql = f"INSERT INTO Users (identity, password, name, sock) VALUES ('{ID}', '{PW}', '{NAME}',0);"
                                self.DBcursor.execute(sql)
                                self.DBconnect.commit()
                                self.DBcursor.execute("SELECT * FROM Users;")
                                A = self.DBcursor.fetchall()
                                print(A)
                                send_header = struct.pack(fmt, b'AS00', 0)
                                print(send_header)
                                self.sock.send(send_header)
                                print(self.sock.send(send_header))
                                sql = f"INSERT INTO SOCK (fd, family, type, proto, ip, port) VALUES (0,'','',0,0,0);"
                                self.DBcursor.execute(sql)
                                self.DBconnect.commit()

                                print('전송 완료')
                            else:
                                print("이름 딴거 해줭")
                                send_header = struct.pack(fmt, b'AFN0', 0)
                                self.sock.send(send_header)
                        else:
                            print('아이디 실패')
                            send_header = struct.pack(fmt, b'AFI0', 0)
                            self.sock.send(send_header)
                        


            except Exception as e:

                exc_type, exc_obj, exc_tb = sys.exc_info()

                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(f'file name: {str(fname)}')
                print(f'error type: {str(exc_type)}')
                print(f'error msg: {str(e)}')
                print(f'line number: {str(exc_tb.tb_lineno)}')
                if self.login == 1:
                    sql = f"UPDATE Users SET sock = 0 WHERE identity = '{self.ID}';"
                    self.DBcursor.execute(sql)
                    self.DBconnect.commit()
                self.sock.close()
                break


port = 8080

serverSock = socket(AF_INET, SOCK_STREAM)
serverSock.bind(('', port))
serverSock.listen(1)

print('%d번 포트로 접속 대기중...' % port)


while True:
    connectionSock, addr = serverSock.accept()
    print(str(addr), '에서 접속 완료')

    receiver = ServerRecv(connectionSock, addr)

    receiver.start()

