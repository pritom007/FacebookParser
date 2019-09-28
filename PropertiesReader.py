from configobj import ConfigObj


class properties:
    def __init__(self, prop="info.properties"):
        self.config = ConfigObj(prop)
        self.email = self.config.get("email")
        self.password = self.config.get("password")
        self.pagename = self.config.get("pagename")
        self.TOTAL_POST_NUMBER = self.config.get("total_post_number")
        self.wishtime = self.config.get("wish_time")
