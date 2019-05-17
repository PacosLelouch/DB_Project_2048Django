数据库为sql server 2008, 
```
connect = pyodbc.connect(
    driver="SQL Server Native Client 10.0",
    server="localhost",
    database="Data_2048",
    uid="testuser",
    pwd="123")
```
第一次使用时需先按上面connect的配置新建数据库，并新建表（详见dbctrl.py的main中的create()）。
```
def create():
    db_ctrl = MyDBCTRL('Data_2048', 'testuser', '123')
    db_ctrl.create_UserInfo()
    db_ctrl.create_LoginRecord()
    db_ctrl.create_Msg()
    db_ctrl.create_PlayRecord()
    db_ctrl.create_HighestScore()
```
首页为xxx/Game_2048/（xxx为服务器地址，如http://localhost:8080/）
