import datetime
import pickle

LOG_FILE = 'log.txt'

"""save to the file the ip and url"""
def saveInLogFile(ip,url):
    with open(LOG_FILE, "a") as file:
        file.write("("+str(datetime.datetime.now())+") "+ ip+" - "+url+'\n')


