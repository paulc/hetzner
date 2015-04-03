
from __future__ import print_function

import base64,json,urllib

try:
    import httplib as client
except ImportError:
    import http.client as client

class HetznerAPIError(Exception):
    pass

ROBOT_URL = "robot-ws.your-server.de"

class HetznerRobot(object):

    def __init__(self,user,password,debug=False):
        self.auth = base64.standard_b64encode(("%s:%s" % (user,password)).encode()).decode()
        self.debug = debug

    def request(self,path,method="GET",params=""):
        conn = client.HTTPSConnection(ROBOT_URL)
        if self.debug:
            conn.set_debuglevel(1)
        headers = { "Authorization": "Basic %s" % self.auth,
                    "Accept": "application/json" }
        if method == "POST":
            headers["Content-type"] = "application/x-www-form-urlencoded"
            params = urllib.urlencode(params)
        conn.request(method,path,params,headers)
        response = conn.getresponse()
        if response.status != 200:
            try:
                error = json.loads(response.read().decode())["error"]
                raise HetznerAPIError("%s %s [%s:%s]" % (response.status,response.reason,
                                                         error["code"],error["message"]))
            except (KeyError,ValueError):
                raise HetznerAPIError("%s %s" % (response.status,response.reason))
        else:
            return json.loads(response.read().decode())

    def server(self,ip):
        return HetznerServer(self,self.request("/server/%s" % ip)["server"]) 

    def servers(self):
        return [ HetznerServer(self,p["server"]) for p in self.request("/server") ]

class HetznerServer(object):

    def __init__(self,robot,params):
        self.robot = robot
        self.ip = params["server_ip"]
        self.params = params

    def get(self,value):
        path = "/%s/%s" % (value,self.ip)
        return self.robot.request(path)[value]

    def post(self,value,params):
        path = "/%s/%s" % (value,self.ip)
        return self.robot.request(path,"POST",params)[value]

    def reset(self,_type='hw'):
        return self.post('reset',{'type':_type})

    def rescue(self,os=None,arch=64,delete=False):
        path = "/boot/%s/rescue" % (self.ip)
        if delete:
            return self.robot.request(path,"DELETE")["rescue"]
        elif os:
            return self.robot.request(path,"POST",{'os':os,'arch':arch})["rescue"]
        else:
            return self.robot.request(path)["rescue"]

    def __repr__(self):
        return "<Server: %s #%d '%s'>" % (self.ip, self.params["server_number"],
                                          self.params["server_name"])

if __name__ == '__main__':
    import code,os.path
    from pprint import pprint as pp
    user,pw = [ x.strip() for x in open(os.path.expanduser("~/.hetzner")).readlines()[:2] ]
    robot = HetznerRobot(user,pw)
    s = robot.servers()
    pp(robot)
    pp(s)
    code.interact(local=locals())
    
