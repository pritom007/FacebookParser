class debug:
    def __init__(self, name=super.__class__, flag=False):
        self.name = name
        self.flag = flag

    def debug_print(self, text):
        """
        Debug print function. Prints debug information with standard print function, if debug=True
        :param text: (str) Debug text
        """
        if not self.flag:
            return
        print(self.name, ": ", str(text))
