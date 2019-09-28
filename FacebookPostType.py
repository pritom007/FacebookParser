from debug import debug

POST_TYPE = "Public Page"

"""
This class is for determing the type of Facebook Posts.
Currently only implemented for "Public Page". Later on will add other posts
"""


class FacebookPostType:

    def __init__(self, post_type=POST_TYPE):
        self.dbag = debug(name=self.__class__, flag=False)
        self.type = post_type

    def public_page_div_path_generator(self, counter=1):
        if self.type == "Public Page":
            main_div = "//div[@class='_1xnd']"
            sub_div = "//div[@class='_4-u2 _4-u8']"
            full_div = counter * main_div + sub_div
            self.dbag.debug_print("Function public_page_div_path_generator\n" + full_div)
            return full_div
        else:
            return


def Test1():
    t = FacebookPostType()
    t.public_page_div_path_generator(1)
