import json
import urllib2
import base64


class TemperaturePersister:
    def __init__(self):
        pass

    def persist(self, items):
        raise NotImplementedError("Should have implemented this")

    @staticmethod
    def get(config):
        key = config["persistence"]["name"]

        if key == "yannickl88":
            return Yannickl88Persister(
                config["persistence"]["url"],
                config["persistence"]["username"],
                config["persistence"]["password"]
            )

        raise IndexError("Unknown key provider key %s given.")


class Yannickl88Persister(TemperaturePersister):
    def __init__(self, url, username, password):
        TemperaturePersister.__init__(self)

        self.url = url
        self.headers = {
            'cache-control': "no-cache",
            'Authorization': 'Basic %s' % base64.b64encode(bytes(username + ':' + password)).decode("ascii")
        }

    def persist(self, items):
        payload = ""
        for item in items:
            payload += "%s %d %d\n" % item

        req = urllib2.Request(self.url, payload, self.headers)
        try:
            response = json.loads(urllib2.urlopen(req).read())

            if not response["success"]:
                print "Server responded with non-success."
                return False

        except urllib2.URLError as e:
            print "Server responded with 500 status."
            return False

        return True
