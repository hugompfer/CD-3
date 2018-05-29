import time

class Cache:
    def __init__(self):
        self.resources=[]
        self.current_milli_time = lambda: int(round(time.time() * 1000))

    """Check if a uri is in cache, returning the content"""
    def check(self,uri):
        resource = self.isInCache(uri)
        if resource != None:
            return resource['content']
        return None

    """update the content of a uri if exists, create a new entry in opossite, and increase the counter"""
    def update(self,uri,content):
        resource= self.isInCache(uri)
        if resource==None:
            resource = {
                'uri': uri,
                'content': content,
                'counter': 0,
                'lastUsed': self.current_milli_time()
            }
            self.resources.append(resource)
        else:
            resource['content']=content

        self.increaseCounter(resource)

    """increase the counter of a rsource and order the list of resources"""
    def increaseCounter(self,resource):
        resource['counter'] =resource['counter']+1
        self.orderList()

    """Order the list of resources per number of the counter and for the tiebreaker last used resource"""
    def orderList(self):
        sort=sorted(self.resources, key = lambda x: (x['counter'],x['lastUsed']),reverse=True)
        for i in range(2,len(sort)):
            sort[i]['content']=None
        self.resources=sort

    """Verify if the uri is in cache, returning the resource dicionary"""
    def isInCache(self,uri):
        for resour in self.resources:
            if resour['uri']==uri:
                return resour
        return None
