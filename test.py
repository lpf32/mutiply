from Parser import ExtendInIParser

if __name__ == "__main__":
    conf = ExtendInIParser()
    conf.read("config.ini")
    print conf._sections
    print conf.options('NAME')
    #print conf.get('NAE', "frui")