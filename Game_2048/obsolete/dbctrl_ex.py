# pip install pyodbc
# pip install pycryptodome
import pyodbc

from Crypto.Cipher import AES
import base64
from binascii import b2a_hex, a2b_hex

SCORES_FOR_NEW_RANK = {
        3:(600, [5]),
        4:(1000, [6]),
        5:(2000, [7]),
        6:(4000, [8]),
    }
# coder = AEScoder()

# 加密密码
class AEScoder():
    def __init__(self):
        self.__encryptKey = "iEpSxImA0vpMUAabsjJWug=="
        self.__key = base64.b64decode(self.__encryptKey)
    # AES加密(utf-8 => utf-8)
    def encrypt(self,data):
        BS = 16
        pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
        cipher = AES.new(self.__key, AES.MODE_ECB)
        encrData = cipher.encrypt(pad(data).encode('utf-8'))
        #encrData = base64.b64encode(encrData)
        return b2a_hex(encrData).decode('utf-8')
    # AES解密(utf-8 => utf-8)
    def decrypt(self,encrData):
        #encrData = base64.b64decode(encrData)
        #unpad = lambda s: s[0:-s[len(s)-1]]
        unpad = lambda s: s[0:-s[-1]]
        cipher = AES.new(self.__key, AES.MODE_ECB)
        decrData = unpad(cipher.decrypt(a2b_hex(encrData.encode('utf-8'))))
        return decrData.decode('utf-8')

# 数据库操作，前缀为aux的为辅助函数
class MyDBCTRL:
    def __init__(self, database, uid, pwd):
        self.database = database
        self.uid = uid
        self.pwd = pwd

    def create_UserInfo(self):
        # 创建UserInfo表，返回Exist, Success, Fail
        # uid: INT IDENTITY(1, 1) [Primary Key]
        # name: VARCHAR(20) UNIQUE NOT NULL
        # password: VARCHAR(96) NOT NULL (password是密文，明文最长30)
        # email: VARCHAR(100) UNIQUE NOT NULL
        # regtime: DATETIME NOT NULL DEFAULT GETDATE()
        conn, cursor = self.aux_connect_sql_server_2008()    # conn - > connect
        if self.aux_check_table_existence(cursor, 'UserInfo'):
            return 'Exist'
        create_UserInfo_str = \
            "CREATE TABLE [UserInfo](" + \
            "uid INT IDENTITY(1, 1), " + \
            "name VARCHAR(20) UNIQUE NOT NULL, " + \
            "password VARCHAR(96) NOT NULL, " + \
            "email VARCHAR(100) UNIQUE NOT NULL, " + \
            "regtime DATETIME NOT NULL DEFAULT GETDATE(), " + \
            "CONSTRAINT PK_UserInfo PRIMARY KEY (uid), " + \
            ");"
        cursor.execute(create_UserInfo_str)
        conn.commit()
        if self.aux_check_table_existence(cursor, 'UserInfo'):
            result = 'Success'
        else:
            result = 'Fail'
        conn.close()
        return result

    def create_LoginRecord(self):
        # 创建LoginRecord表，返回Exist, Success, Fail
        # loginid: INT IDENTITY(1, 1) [Primary Key]
        # logintime: DATETIME NOT NULL DEFAULT GETDATE()
        # uid: INT [Foreign Key: UserInfo] CASCADE
        conn, cursor = self.aux_connect_sql_server_2008()
        if self.aux_check_table_existence(cursor, 'LoginRecord'):
            return 'Exist'
        create_LoginRecord_str = \
            "CREATE TABLE LoginRecord(" + \
            "loginid INT IDENTITY(1, 1), " + \
            "logintime DATETIME NOT NULL DEFAULT GETDATE(), " + \
            "uid INT NOT NULL, " + \
            "CONSTRAINT PK_LoginRecord PRIMARY KEY (loginid), " + \
            "CONSTRAINT FK_LoginRecord_uid FOREIGN KEY (uid) REFERENCES [UserInfo](uid) on delete CASCADE, " + \
            ");"
        cursor.execute(create_LoginRecord_str)
        conn.commit()
        if self.aux_check_table_existence(cursor, 'LoginRecord'):
            result = 'Success'
        else:
            result = 'Fail'
        conn.close()
        return result

    def create_PlayRecord(self):
        # 创建PlayRecord表，返回Exist, Success, Fail
        # rcid: INT IDENTITY(1, 1) [Primary Key]
        # playtime: DATETIME NOT NULL DEFAULT GETDATE()
        # rank: TINYINT NOT NULL (棋盘大小，3到8)
        # score: INT NOT NULL >=0
        # uid: INT [Foreign Key: UserInfo] CASCADE
        conn, cursor = self.aux_connect_sql_server_2008()
        if self.aux_check_table_existence(cursor, 'PlayRecord'):
            return 'Exist'
        create_PlayRecord_str = \
            "CREATE TABLE PlayRecord(" + \
            "rcid INT IDENTITY(1, 1), " + \
            "playtime DATETIME NOT NULL DEFAULT GETDATE(), " + \
            "rank TINYINT NOT NULL, " + \
            "score INT NOT NULL, " + \
            "uid INT NOT NULL, " + \
            "CONSTRAINT PK_PlayRecord PRIMARY KEY (rcid), " + \
            "CONSTRAINT FK_PlayRecord_uid FOREIGN KEY (uid) REFERENCES [UserInfo](uid) on delete CASCADE, " + \
            "CHECK (score>=0), " + \
            ");"
        cursor.execute(create_PlayRecord_str)
        conn.commit()
        if self.aux_check_table_existence(cursor, 'PlayRecord'):
            result = 'Success'
        else:
            result = 'Fail'
        conn.close()
        return result
        #TODO

    def create_Msg(self):
        # 创建Msg表，返回Exist, Success, Fail
        # msgid: INT IDENTITY(1, 1) [Primary Key]
        # msgtime: DATETIME NOT NULL DEFAULT GETDATE()
        # msgtext: NVARCHAR(300) NOT NULL (最多留言300字)
        # uid: INT [Foreign Key: UserInfo] CASCADE
        conn, cursor = self.aux_connect_sql_server_2008()
        if self.aux_check_table_existence(cursor, 'Msg'):
            return 'Exist'
        create_Msg_str = \
            "CREATE TABLE Msg(" + \
            "msgid INT IDENTITY(1, 1), " + \
            "msgtime DATETIME NOT NULL DEFAULT GETDATE(), " + \
            "msgtext NVARCHAR(300) NOT NULL, " + \
            "uid INT NOT NULL, " + \
            "CONSTRAINT PK_Msg PRIMARY KEY (msgid), " + \
            "CONSTRAINT FK_Msg_uid FOREIGN KEY (uid) REFERENCES [UserInfo](uid) on delete CASCADE, " + \
            ");"
        cursor.execute(create_Msg_str)
        conn.commit()
        if self.aux_check_table_existence(cursor, 'Msg'):
            result = 'Success'
        else:
            result = 'Fail'
        conn.close()
        return result
        #TODO

    def create_HighestScore(self):
        # 创建HighestScore表，返回Exist, Success, Fail
        # hsid: INT IDENTITY(1, 1) [Primary Key]
        # rank: TINYINT NOT NULL CHECK (rank>=3 AND rank<=8) (棋盘大小，3到8)
        # uid: INT NOT NULL [Foreign Key: UserInfo] CASCADE
        # rcid: INT [Foreign Key: PlayRecord]
        # 给PlayRecord表新增Trigger，过程为：
        #  在PlayRecord表中插入rank,score,uid，
        #  在HighestScore中查找uid=inserted.uid, rank=inserted.rank的记录x，
        #  若x.rcid为空，或x.rcid.score<score，则修改x.rcid <- new_rcid.
        conn, cursor = self.aux_connect_sql_server_2008()
        if not self.aux_check_table_existence(cursor, 'PlayRecord'):
            return 'Fail'
        if self.aux_check_table_existence(cursor, 'HighestScore'):
            return 'Exist'
        create_HighestScore_str = \
            "CREATE TABLE HighestScore(" + \
            "hsid INT IDENTITY(1, 1), " + \
            "rank TINYINT NOT NULL CHECK (rank>=3 AND rank<=8), " + \
            "uid INT NOT NULL, " + \
            "rcid INT, " + \
            "CONSTRAINT PK_HIGH_Record PRIMARY KEY (hsid), " + \
            "CONSTRAINT FK_HIGH_Record_rcid FOREIGN KEY (rcid) REFERENCES PlayRecord(rcid), " + \
            "CONSTRAINT FK_HIGH_Record_uid FOREIGN KEY (uid) REFERENCES UserInfo(uid), " + \
            ");"
        cursor.execute(create_HighestScore_str)
        create_PlayRecord_trigger_str = \
            "CREATE TRIGGER UPDATE_HIGHEST ON PlayRecord " + \
            "FOR INSERT AS " + \
            "BEGIN " + \
            "DECLARE @hsid INT; " + \
            "DECLARE @old_rcid INT; " + \
            "SELECT @hsid=hsid, @old_rcid=rcid FROM HighestScore WHERE " + \
            "uid=(SELECT uid FROM inserted) AND " + \
            "rank=(SELECT rank FROM inserted);" + \
            "IF (" + \
            "@old_rcid IS NULL" + \
            ") OR (" + \
            "(SELECT score FROM PlayRecord WHERE rcid=@old_rcid)" + \
            "<(SELECT score FROM inserted)" + \
            ")" + \
            "  BEGIN " + \
            "  UPDATE HighesetScore SET rcid=(SELECT rcid FROM inserted)" + \
            "  WHERE hsid=@hsid;" + \
            "  END " + \
            "END"
        cursor.execute(create_PlayRecord_trigger_str)
        conn.commit()
        if self.aux_check_table_existence(cursor, 'HighestScore'):
            result = 'Success'
        else:
            result = 'Fail'
        conn.close()
        return result

    def add_new_user(self, name, psw, email):
        # 在UserInfo表中插入name=name, password=psw, email=email, regtime=GETDATE()，
        # 在HighestScore插入rank=3, rcid=NULL，
        # 在HighestScore插入rank=4, rcid=NULL。
        try:
            conn, cursor = self.aux_connect_sql_server_2008()
            """插入UserInfo"""
            add_new_user_str = \
                "INSERT INTO UserInfo (name, password, email) VALUES" + \
                "(?, ?, ?);"
            cursor.execute(add_new_user_str, name, psw, email)

            
            find_uid_str = \
                "SELECT uid FROM UserInfo WHERE name=?;"
            cursor.execute(find_uid_str, name)
            uid = cursor.fetchall()[0][0]
            
            add_new_rank_str = \
                "INSERT INTO HighestScore (rank, uid, rcid) " + \
                "VALUES (?, ?, NULL);"
            cursor.execute(add_new_rank_str, 3, uid)
            cursor.execute(add_new_rank_str, 4, uid)
            conn.commit()

            conn.close()
        except Exception as e:
            print(e.__str__())
            return (False, e.__str__())
        return (True, '')
        #TODO

    def add_login_record(self, name):
        # 在LoginRecord表中插入uid=(a.uid where a.name=name)。
        try:
            conn, cursor = self.aux_connect_sql_server_2008()
            # 查uid
            find_uid_str = \
                "SELECT uid FROM UserInfo WHERE name=?;"
            cursor.execute(find_uid_str, name)
            uid = cursor.fetchall()[0][0]

            add_login_record_str = \
                "INSERT INTO LoginRecord (uid) " + \
                "VALUES (?);"
            cursor.execute(add_login_record_str, uid)
            conn.commit()
            conn.close()
        except Exception as e:
            print(e.__str__())
            return (False, e.__str__())
        return (True, '')
        #TODO

    def add_play_record(self, name, rank, score, scores_for_new_rank=SCORES_FOR_NEW_RANK):
        # 在PlayRecord表中插入rank=rank, score=score, uid=(a.uid where a.name=name)，
        # 然后（trigger执行后）根据rank和score判断是否可以解锁new_rank（解锁条件在scores_for_new_rank中)，
        # 如果score足够，则在新rank列表中遍历new_rank（因为new_rank写在列表里），
        # 在HighestScore中查找uid=(a.uid where a.name=name), rank=new_rank的记录，
        # 若没有，则插入有new_rank的新记录。
        # （下面是scores_for_new_rank的说明）
        # scores_for_new_rank: dict.
        # key: current rank, value: (min score, [new rank1, new rank2, ...]).
        # e.g. 6:(4000, [7, 8]).
        try:
            conn, cursor = self.aux_connect_sql_server_2008()
            # 查uid
            find_uid_str = \
                "SELECT uid FROM UserInfo WHERE name=?;"
            cursor.execute(find_uid_str, name)
            uid = cursor.fetchall()[0][0]
            """插入PlayRecord"""
            add_play_record_str = \
                "INSERT INTO PlayRecord (rank, score, uid) VALUES" + \
                "(?, ?, ?);"
            cursor.execute(add_play_record_str, rank, score, uid)
            # 插入HighestScore
            min_score, new_rank_list = scores_for_new_rank[rank]
            if score >= min_score:
                for new_rank in new_rank_list:
                    find_new_rank_str = \
                        "SELECT * FROM HighestScore " + \
                        "WHERE uid=? AND rank=?;"
                    cursor.execute(find_new_rank_str, uid, new_rank)
                    new_highest_score = cursor.fetchall()
                    if new_highest_score == []:
                        add_new_rank_str = \
                            "INSERT INTO HighestScore (rank, uid, rcid) " + \
                            "VALUES (?, ?, NULL);"
                        cursor.execute(add_new_rank_str, new_rank, uid)
            cursor.commit() # COMMIT TRANSACTION
            conn.close()
        except Exception as e:
            return (False, e.__str__())
        
        return (True, '')

    def add_message(self, name, message):
        # 在Msg中插入留言信息，name=name, message=message。
        try:
            conn, cursor = self.aux_connect_sql_server_2008()
            find_uid_str = \
                "SELECT uid FROM UserInfo WHERE name=?;"
            cursor.execute(find_uid_str, name)
            uid = cursor.fetchall()[0][0]
            add_message_str = \
                "INSERT INTO Msg (msgtext, uid) VALUES (?, ?);"
            cursor.execute(add_message_str, message, uid)
            cursor.commit()
            conn.close()
        except Exception as e:
            return (False, e.__str__())
        return (True, '')

    def show_play_record(self, name):
        # 在PlayRecord中查找所有该玩家的游戏记录，name, rank, score, playtime，
        # 返回最近10条。
        conn, cursor = self.aux_connect_sql_server_2008()
        find_play_record_str = \
            "SELECT (name, rank, score, playtime) FROM " + \
            "PlayRecord INNER JOIN UserInfo ON PlayerRecord.uid=UserInfo.uid " + \
            "WHERE name=? ORDER BY playtime DESC;"
        cursor.execute(find_play_record_str, name)
        result = cursor.fetchmany(10)
        conn.close()
        return result

    def show_info(self, name):
        # 在UserInfo中查找该玩家的除密码外的记录。
        # 返回该记录
        conn, cursor = self.aux_connect_sql_server_2008()
        find_player_str = \
            "SELECT (uid, name, email, regtime) FROM " + \
            "UserInfo WHERE name=?;"
        cursor.execute(find_player_str, name)
        result = cursor.fetchone()
        conn.close()
        return result

    def check_login(self, name, pwd):
        # 在UserInfo中根据name, password查找该玩家的的记录，用于检查登录。
        # 返回是否存在该记录
        conn, cursor = self.aux_connect_sql_server_2008()
        find_player_str = \
            "SELECT uid FROM " + \
            "UserInfo WHERE name=? AND password=?;"
        cursor.execute(find_player_str, name, pwd)
        result = cursor.fetchone()
        conn.close()
        return len(result) == 1

    def check_register(self, name, email):
        # 在UserInfo中根据name, email任一信息查找该玩家的的记录，用于检查注册。
        # 返回是否不存在该记录
        conn, cursor = self.aux_connect_sql_server_2008()
        find_player_str = \
            "SELECT uid FROM " + \
            "UserInfo WHERE name=? OR email=?;"
        cursor.execute(find_player_str, name, email)
        result = cursor.fetchone()
        conn.close()
        return len(result) == 0

    def show_message(self):
        # 在Msg中查找所有玩家的留言信息，name, msgtext, msgtime，
        # 返回最近50条。
        conn, cursor = self.aux_connect_sql_server_2008()
        find_message_str = \
            "SELECT (name, msgtext, msgtime) FROM " + \
            "Msg INNER JOIN UserInfo ON Msg.uid=UserInfo.uid ORDER BY msgtime DESC;"
        cursor.execute(find_message_str)
        return cursor.fetchmany(50)

    def show_login_record(self, name):
        # 在LoginRecord中查找所有该玩家的登录记录，name, logintime，
        # 返回最近10条。
        conn, cursor = self.aux_connect_sql_server_2008()
        
        find_uid_str = \
            "SELECT uid FROM UserInfo WHERE name=?;"
        cursor.execute(find_uid_str, name)
        uid = cursor.fetchall()[0][0]

        find_login_record_str = \
            "SELECT loginid, name, logintime FROM " + \
            "LoginRecord INNER JOIN UserInfo ON UserInfo.uid=LoginRecord.uid WHERE UserInfo.uid=? ORDER BY logintime DESC;"
        cursor.execute(find_login_record_str, uid)
        return cursor.fetchmany(10)

        # TODO
        
    def show_score_board(self, rank):
        # 在PlayRecord中查找该rank下的name, score, playtime, 按score降序排列
        # 返回最高50条。

        conn, cursor = self.aux_connect_sql_server_2008()

        find_score_board_str = \
            "SELECT name, score, playtime FROM " + \
            "PlayRecord INNER JOIN UserInfo ON UserInfo.uid=PlayRecord.uid WHERE rank=? ORDER BY score DESC;"
        cursor.execute(find_score_board_str, rank)
        return cursor.fetchmany(50)

        # TODO
        
    def aux_connect_sql_server_2008(self):
        # 辅助函数：连接sql server 2008数据库。
        connect = pyodbc.connect(
            driver="SQL Server Native Client 10.0",
            server="localhost",
            database=self.database,
            uid=self.uid,
            pwd=self.pwd)
        cursor = connect.cursor()
        return connect, cursor

    def aux_check_table_existence(self, cursor, table_name):
        # 辅助函数：判断表是否已存在。
        for table_info in cursor.tables(tableType='TABLE'):
            if table_info.table_name == table_name:
                return True
        return False

if __name__ == "__main__":
    def test_AES(s='qwertyuiopp[]asdfghjkl;zxcvbnm,fnbsldkfgdfjvlncxl;bnfdsgujt./'):
        ac = AEScoder()
        b = ac.encrypt(s)
        s1 = ac.decrypt(b)
        print(s)
        print(b, len(b))
        print(s1, len(s1))
    #test_AES()
    # 我自己新建的数据库叫Data_2048，用户名testuser，密码123. 
    #db_ctrl = MyDBCTRL('DATA_2019', 'admin', '123')
    # your test code here

    def MY_TEST(db_ctrl):
        db_ctrl.create_UserInfo()
        db_ctrl.create_LoginRecord()
        db_ctrl.create_Msg()
        db_ctrl.create_PlayRecord()
        db_ctrl.create_HighestScore()
        
        
        # db_ctrl.add_new_user('zhangsan', '123456', '2662495174@qq.com')
        # db_ctrl.add_new_user('lisi', '123456', '2662495174@qq.com')

        # db_ctrl.add_login_record('zhangsan')
        # db_ctrl.add_login_record('lisi')
        # db_ctrl.add_login_record('zhangsan')
        # db_ctrl.add_login_record('zhangsan')

        db_ctrl.add_message('ss', 'fhasdoifhasdhg')
        db_ctrl.add_message('zhangsan', 'wo hen shuai')
        
        a = db_ctrl.show_login_record('zhangsan')
        print(a)
        b = db_ctrl.show_login_record('lisi')
        print(b)
        c = db_ctrl.show_score_board(3)
        print(c)
    
    MY_TEST(db_ctrl)
        



        

        



    pass
