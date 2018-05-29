class Authenticator:
    def __init__(self):
        self.users={}


    def login(self,ip,username,password):
        user=self.getUser(ip)
        if user==None:
            self.users[ip]={
                'username':username,
                'password':password,
                'logged':'1'}
            return True
        else:
            if user['username']==username and user['password']==password:
                user['logged'] = '1'
                return True
            return False

    def getUser(self,ip):
        try:
            return self.users[ip]
        except:
            return None

    def logout(self,ip):
        user = self.getUser(ip)
        if user==None or user['logged']=='0':
            return False
        else:
            user['logged'] = '0'
            return True

    def isRegistered(self,ip):
        try:
            user=self.users[ip]
            return True
            return False
        except:
            return False


    def isAutenticate(self,ip):
        try:
            user=self.users[ip]
            if user['logged']=="1":
                return True
            return False
        except:
            return False