from .entities.user import User

class ModelUser():
    
    @classmethod
    def login(self, mysql, user):
        try:
            
            sql="SELECT id, username, password, fullname FROM login WHERE username = '{}'".format(user.username)
            
            conn=mysql.connect()
            cursor=conn.cursor()
            cursor.execute(sql)
            row=cursor.fetchone()
            if row != None:
                user=User(row[0], row[1], User.check_password(row[2], user.password), row[3])
                return user
            else:
                return None
            
            
        except Exception as e:
            raise Exception(e)
        
    @classmethod
    def get_by_id(self, mysql, id):
        try:
            
            sql="SELECT id, username, fullname FROM login WHERE id = '{}'".format(id)
            
            conn=mysql.connect()
            cursor=conn.cursor()
            cursor.execute(sql)
            row=cursor.fetchone()
            if row != None:
                return User(row[0], row[1], None, row[2])
                 
            else:
                return None
            
            
        except Exception as e:
            raise Exception(e)