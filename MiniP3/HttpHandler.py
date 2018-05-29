import json
import FilesUtil
import datetime
from Cache import *
import time
from Authenticator import *
from Error import *
import os
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime

class HtppHandler:
    def __init__(self):
        self.methods=['GET','POST','HEAD','PUT','DELETE']
        self.imagesSupported=['jpg','png','gif']
        self.mimeTypes = {'jpg': 'image/jpeg', 'png': 'image/png', 'gif': 'image/gif', 'html': 'text/html','mp3':'audio/mpeg','mp4':'video/mp4','application/x-www-form-urlencoded':'application/json'}
        self.status = {'404': 'HTTP/1.1 404 Not Found', '400': 'HTTP/1.1  400 Bad Request', '403': 'HTTP/1.1  403 Forbidden','200':'HTTP/1.1 200 OK'}
        self.cache=Cache()
        self.authenticator=Authenticator()
        self.timeout=10

    """ Method to handle the request from client"""
    def handleRequest(self,request,clientIP):
        try:
            dicRequest=self.parseRequest(request)
            FilesUtil.saveInLogFile(clientIP, dicRequest['path'])
            if dicRequest['method']=='GET':
                return self.doGET(dicRequest,clientIP)
            elif dicRequest['method']=='POST':
                return self.doPOST(dicRequest,clientIP);
            elif dicRequest['method']=='HEAD':
                return self.doHEAD(dicRequest);
            elif dicRequest['method']=='PUT':
                return self.doPUT(dicRequest,clientIP);
            elif dicRequest['method']=='DELETE':
                return self.doDELETE(dicRequest,clientIP);
            else:
                return self.errorResponse('400')
        except Exception as codeError:
            if str(codeError) in self.status.keys():
                return self.errorResponse(str(codeError))
            return self.errorResponse('400')

    """parse the request to a dicionary"""
    def parseRequest(self,request):
        try:
            lines=request.splitlines()
            index=lines.index("") if "" in lines else len(lines)
            headers=lines[1:index]
            body=lines[index+1:]
            method,path,version = lines[0].split()
            if not method in self.methods or  version.upper()!='HTTP/1.1':
                raise Error('400')

            dic={
                'method':method,
                'path':path,
                'version':version,
                'headers':{},
                'body':body[0] if len(body)>0 else ''
            }

            for i in range(0,len(headers)):
                title,content=headers[i].split(':',1)
                dic['headers'][title]=content.strip(' ')

            return dic
        except :
            raise Error('400')

    """handle the request to a get method"""
    def doGET(self,dicRequest,clientIP):
        path = self.getCorrectPath(dicRequest['path'])
        if 'htdocs/private/' in path and not self.authenticator.isAutenticate(clientIP):
            return self.errorResponse('403')
        elif '/extras/logout' in path:
            return self.logout(path,dicRequest,clientIP)
        elif '/extras/translate' in path:
            return self.translate(dicRequest,path)
        else:
            return self.response('200',self.getResource(dicRequest,path), path, dicRequest)

    """translate the message body receive to accept-language received"""
    def translate(self,dicRequest,path):
        dicRequest['headers']['Accept-Language']=dicRequest['headers'].get('Accept-Language','pt-PT')
        language=dicRequest['headers']['Accept-Language'].split(',')[0]
        if 'en-US' in language:
            return self.response('200', 'hello'.encode(), path, dicRequest)
        elif 'pt-PT' in language:
            return self.response('200', 'ola'.encode(), path, dicRequest)
        else:
            return self.response('200', 'Language not suported'.encode(), path, dicRequest)

    """Get resource from a path if it is not in cache"""
    def getResource(self,dicRequest,path):
        try:
            resource = self.cache.check(dicRequest['path'])
            if resource == None:
                time.sleep(1)
                with open(path, 'rb') as content_file:
                    resource = content_file.read()

            self.cache.update(dicRequest['path'], resource)

            return resource
        except:
            raise Error('404')

    """handle the request to a HEAD method"""
    def doHEAD(self,dicRequest):
        path = self.getCorrectPath(dicRequest['path'])
        resource=self.getResource(dicRequest,path)
        return self.response('200', resource, path, dicRequest)

    """get the 2 firt values from a dicionary"""
    def getCredetentials(self,dic):
        username=""
        password=""
        i=0
        for key in dic.keys():
            if i>=2:
                return username,password
            elif i==0:
                username=dic[key]
            else:
                password=dic[key]
            i+=1
        return username,password

    """handle the request to a POST method"""
    def doPOST(self,dicRequest,clientIP):
        response = self.createResponseDic(self.status['200'])
        if "/extras/login" == dicRequest['path']:
            credentials=self.getPOSTBody(dicRequest['body'])
            username,password=self.getCredetentials(credentials)
            if self.authenticator.login(clientIP,username,password):
                response['body'] = 'Logado'.encode()
            else:
                response['body'] = 'Credenciais erradas'.encode()
            response['headers']['Content-Type']=self.mimeTypes['html']
        else:
            response['headers']['Content-Type'] = self.mimeTypes[dicRequest['headers'].get('Content-Type','html')]
            #response['headers']['Content-Type'] = self.mimeTypes[dicRequest['headers']['Content-Type']]
            if 'application/json' in response['headers']['Content-Type']:
                response['body'] = json.dumps(self.getPOSTBody(dicRequest['body'])).encode()
            else:
                response['body'] = dicRequest['body'].encode()

        #como e suposto fazer se nao for um formulario
        response['headers']['Content-Length'] = len(response['body'])

        return self.toString(response)

    """Parse the request body to a dicionary"""
    def getPOSTBody(self,information):
        body={}
        separation = information.split('&')
        for i in range(0,len(separation)):
            inf=separation[i].split('=')
            body[inf[0]]=inf[1] if len(inf)>0 else b""
        return body

    """handle the request to a DELETE method"""
    def doDELETE(self,dicRequest,clientIP):
        filename = self.getCorrectPath(dicRequest['path'])
        if self.authenticator.isAutenticate(clientIP) and '/extras/files/' in filename:
            try:
                os.remove(filename)
                return self.response('200', 'Ficheiro apagado'.encode(), filename, dicRequest)
            except :
                raise Error('404')
        else:
            raise Error('403')

    """handle the request to a PUT method"""
    def doPUT(self,dicRequest,clientIP):
        if self.authenticator.isAutenticate(clientIP)==True:
            try:
                time=int(dicRequest['body'].split('=')[1])
            except:
                raise Error('400')
            self.timeout=time
            return self.response('200', 'Time alterado com sucesso'.encode(), self.getCorrectPath(dicRequest['path']), dicRequest)
        else:
            raise Error('403')

    """Logout of a user"""
    def logout(self,path,dicRequest,clientIP):
        if self.authenticator.logout(clientIP):
            return self.response('200', 'Logout efetuado com sucesso'.encode(), path, dicRequest)
        else:
            return self.response('200', 'Não estas logado.'.encode(), path, dicRequest)

    """Check if the name passed is an image"""
    def isImage(self, name):
        for img in self.imagesSupported:
            if name.__contains__(img):
                return True
        return False

    """Gets the correct path to fetch the resource"""
    def getCorrectPath(self,path):
        if path=='/' or 'index.html' in path:
            return 'htdocs/index.html'
        elif self.isImage(path) or 'extras' in path or 'private' in path:
            return 'htdocs'+path
        else:
            return 'htdocs'+path

    """Function that has the responsibility of creating the client response"""
    def response(self,status,information,path,dicRequest):
        try:
            responseDic=self.createResponseDic(self.status[status])
            try:
                responseDic['headers']['Content-Type']=self.mimeTypes[path[path.index('.')+1:]]
            except:
                responseDic['headers']['Content-Type'] = self.mimeTypes['html']

            responseDic['headers']['Content-Length'] = len(information)

            if 'Connection' in dicRequest['headers'].keys() :
                responseDic['headers']['Connection']=dicRequest['headers']['Connection']

            if dicRequest and dicRequest['method']!='HEAD':
                responseDic['body']=information

            return self.toString(responseDic)
        except:
            raise Error('400')

    """Create a error response formated"""
    def errorResponse(self,status):
        strInformation = self.status[status]
        responseDic = self.createResponseDic(strInformation)
        bytesInformation=strInformation.encode()
        responseDic['headers']['Content-Type'] = 'text/html'
        responseDic['headers']['Content-Length'] = len(bytesInformation)
        responseDic['body']=bytesInformation
        return self.toString(responseDic)

    """Create the default response dicionary"""
    def createResponseDic(self,status):
        dic= {
            'status':status,
            'headers':{
                'Content-Type':'',
                'Content-Length':'',
                'Date':format_date_time(mktime(datetime.now().timetuple())),
                'Connection':'keep-alive'
            },
            'body':''.encode()
        }

        return dic

    """Convert the response dicionary to string to send to the client"""
    def toString(self,dicResponse):
        info=(dicResponse['status']+'\n').encode()
        for name,value in dicResponse['headers'].items():
            info += (name + ':' + str(value)+'\n').encode()
        info+='\n'.encode()+dicResponse['body']
        return info,dicResponse['headers']['Connection']


