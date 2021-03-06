# pip install pyodbc
# pip install pycryptodome
import pyodbc

from Crypto.Cipher import AES
import base64
from binascii import b2a_hex, a2b_hex

SCORES_FOR_NEW_RANK = {
        4:(1000, [5]),
        5:(2000, [6]),
        6:(4000, [7, 8]),
    }

# 加密密码
class AEScoder:
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

    def create_User(self):
        # 创建User表，返回Exist, Success, Fail
        # uid: INT IDENTITY(1, 1) [Primary Key]
        # name: VARCHAR(20) UNIQUE NOT NULL
        # password: VARCHAR(96) NOT NULL (password是密文，明文最长30)
        # email: VARCHAR(60) NOT NULL
        # regtime: DATETIME NOT NULL DEFAULT GETDATE()
        connect, cursor = self.aux_connect_sql_server_2008()
        if self.aux_check_table_existence(cursor, 'User'):
            return 'Exist'
        create_User_str = \
            "CREATE TABLE User(" + \
            "uid INT IDENTITY(1, 1), " + \
            "name VARCHAR(20) UNIQUE NOT NULL, " + \
            "password VARCHAR(96) NOT NULL, " + \
            "email VARCHAR(60) NOT NULL, " + \
            "regtime DATETIME NOT NULL DEFAULT GETDATE(), " + \
            "CONSTRAINT PK_User PRIMARY KEY (uid), " + \
            ");"
        cursor.execute(create_User_str)
        conn.commit()
        if self.aux_check_table_existence(cursor, 'User'):
            result = 'Success'
        else:
            result = 'Fail'
        conn.close()
        return result

    def create_LoginRecord(self):
        # 创建LoginRecord表，返回Exist, Success, Fail
        # loginid: INT IDENTITY(1, 1) [Primary Key]
        # logintime: DATETIME NOT NULL DEFAULT GETDATE()
        # uid: INT [Foreign Key: User] SET NULL
        conn, cursor = self.aux_connect_sql_server_2008()
        if self.aux_check_table_existence(cursor, 'LoginRecord'):
            return 'Exist'
        create_LoginRecord_str = \
            "CREATE TABLE LoginRecord(" + \
            "loginid INT IDENTITY(1, 1), " + \
            "logintime DATETIME NOT NULL DEFAULT GETDATE(), " + \
            "uid INT NOT NULL, " + \
            "CONSTRAINT PK_LoginRecord PRIMARY KEY (loginid), " + \
            "CONSTRAINT FK_LoginRecord_uid FOREIGN KEY (uid) REFERENCES User(uid), " + \
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
        # score: INT NOT NULL
        # uid: INT [Foreign Key: User] SET NULL

        #TODO

    def create_Msg(self):
        # 创建Msg表，返回Exist, Success, Fail
        # msgid: INT IDENTITY(1, 1) [Primary Key]
        # msgtime: DATETIME NOT NULL DEFAULT GETDATE()
        # msgtext: NVARCHAR(300) NOT NULL (最多留言300字)
        # uid: INT [Foreign Key: User] SET NULL

        #TODO

    def create_HighestScore(self):
        # 创建HighestScore表，返回Exist, Success, Fail
        # hsid: INT IDENTITY(1, 1) [Primary Key]
        # rank: TINYINT NOT NULL CHECK (rank>=3 AND rank<=8) (棋盘大小，3到8)
        # uid: INT NOT NULL [Foreign Key: User] CASCADE
        # rcid: INT [Foreign Key: PlayRecord] SET NULL

        #TODO

    def add_new_user(self, name, psw, email):
        # 在User表中插入name=name, password=psw, email=email, regtime=GETDATE()，
        # 在HighestScore插入rank=3, rcid=NULL，
        # 在HighestScore插入rank=4, rcid=NULL。

        #TODO

    def add_login_record(self, name):
        # 在LoginRecord表中插入uid=(a.uid where a.name=name)。

        #TODO

    def add_play_record(self, name, rank, score, scores_for_new_rank=SCORES_FOR_NEW_RANK):
        # 在PlayRecord表中插入rank=rank, score=score, uid=(a.uid where a.name=name)，
        # 在HighestScore中查找uid=(a.uid where a.name=name), rank=rank的记录x，
        # 若x.rcid为空，或x.rcid.score<score，则修改x.rcid <- new rcid，
        # 然后根据rank和score判断是否可以解锁new_rank（解锁条件在scores_for_new_rank中)，
        # 如果score足够，则在新rank列表中遍历new_rank（因为new_rank写在列表里），
        # 在HighestScore中查找uid=(a.uid where a.name=name), rank=new_rank的记录，
        # 若没有，则插入有new_rank的新记录。
        # （下面是scores_for_new_rank的说明）
        # scores_for_new_rank: dict.
        # key: current rank, value: (min score, [new rank1, new rank2, ...]).
        # e.g. 6:(4000, [7, 8]).
        conn, cursor = self.aux_connect_sql_server_2008()
        # 查uid
        find_uid_str = \
            "SELECT uid FROM User WHERE name='%s';"%name
        cursor.execute(find_uid_str)
        uid = cursor.fetchall()[0][0]
        """插入PlayRecord"""
        add_play_record_str = \
            "INSERT INTO PlayRecord (rank, score) VALUES" + \
            "(%d, %d, %d);"%(rank, score, uid)
        cursor.execute(add_play_record_str)
        #cursor.commit() # Do not commit
        cursor.execute("SELECT SCOPE_IDENTITY();") # 获取最新插入的标识
        new_rcid = int(cursor.fetchall()[0][0])
        # 修改HighestScore
        update_highest_score_flag = False
        find_highest_rcid_str = \
            "SELECT hsid, rcid FROM HighestScore " + \
            "WHERE uid=%d AND rank=%d;"%(uid, rank)
        cursor.execute(find_highest_score_str)
        hsid, rcid = cursor.fetchall()[0]
        if rcid is None:
            update_highest_score_flag = True
        else:
            find_score_str = \
                "SELECT score FROM PlayRecord " + \
                "WHERE rcid=%d;"%(rcid)
            cursor.execute(find_score_str)
            highest_score = cursor.fetchall()[0][0]
            if score > highest_score:
                update_highest_score_flag = True
        if update_highest_score_flag:
            save_new_highest_score_str = \
                "UPDATE HighestScore SET rcid=%d "%new_rcid + \
                "WHERE hsid=%d;"%hsid
            cursor.execute(save_new_highest_score_str)
            #cursor.commit() # Do not commit
            # 插入HighestScore
            min_score, new_rank_list = scores_for_new_rank[rank]
            if score >= min_score:
                for new_rank in new_rank_list:
                    find_new_rank_str = \
                        "SELECT * FROM HighestScore " + \
                        "WHERE uid=%d AND rank=%d;"%(uid, new_rank)
                    cursor.execute(find_new_rank_str)
                    new_highest_score = cursor.fetchall()
                    if new_highest_score == []:
                        add_new_rank_str = \
                            "INSERT INTO HighestScore (rank, uid, rcid) " + \
                            "VALUES (%d, %d, NULL);"%(new_rank, uid)
                        cursor.execute(add_new_rank_str)
                        #cursor.commit() # Do not commit
        cursor.commit() # COMMIT TRANSACTION
        conn.close()

    def add_message(self, name, message):
        # 在Msg中插入留言信息，name=name, message=message。
        conn, cursor = self.aux_connect_sql_server_2008()
        find_uid_str = \
            "SELECT uid FROM User WHERE name='%s';"%name
        cursor.execute(find_uid_str)
        uid = cursor.fetchall()[0][0]
        add_message_str = \
            "INSERT INTO Msg (msgtext, uid) VALUES ('%s', %d);"%(message, uid)
        cursor.execute(add_message_str)
        cursor.commit()
        conn.close()

    def show_play_record(self, name):
        # 在PlayRecord中查找所有该玩家的游戏记录，name, rank, score, playtime，
        # 返回最近10条。
        conn, cursor = self.aux_connect_sql_server_2008()
        find_play_record_str = \
            "SELECT (name, rank, score, playtime) FROM " + \
            "PlayRecord INNER JOIN User ON PlayerRecord.uid=User.uid " + \
            "WHERE name='%s' ORDER BY playtime DESC;"%name
        cursor.execute(find_play_record_str)
        result = cursor.fetchmany(10)
        conn.close()
        return result

    def show_info(self, name):
        # 在User中查找该玩家的除密码外的记录。
        # 返回该记录
        conn, cursor = self.aux_connect_sql_server_2008()
        find_player_str = \
            "SELECT (uid, name, email, regtime) FROM " + \
            "User WHERE name='%s';"%name
        cursor.execute(find_player_str)
        result = cursor.fetchall()[0]
        conn.close()
        return result

    def show_message(self):
        # 在Msg中查找所有玩家的留言信息，name, msgtext, msgtime，
        # 返回最近50条。
        conn, cursor = self.aux_connect_sql_server_2008()
        find_message_str = \
            "SELECT (name, msgtext, msgtime) FROM " + \
            "Msg INNER JOIN User ON Msg.uid=User.uid ORDER BY msgtime DESC;"
        cursor.execute(find_message_str)
        return cursor.fetchmany(50)

    def show_login_record(self, name):
        # 在LoginRecord中查找所有该玩家的登录记录，name, logintime，
        # 返回最近10条。

        # TODO

    def show_score_board(self, rank):
        # 在PlayRecord中查找该rank下的name, score, playtime, 按score降序排列
        # 返回最高50条。

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
    db_ctrl = MyDBCTRL('Data_2048', 'testuser', '123')
    # your test code here
    pass
