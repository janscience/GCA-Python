import netrc


class UPAuth(object):
    def __init__(self, user, password):
        self.user = user
        self.password = password

    def get_credentials(self, host):
        return self.user, self.password


class NetRCAuth(object):
    def __init__(self, path=None):
        self.path = path

    def get_credentials(self, host):
        rc = netrc.netrc(self.path)
        login, account, password = rc.authenticators(host)
        return login, password