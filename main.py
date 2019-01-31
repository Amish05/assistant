import os
import re
import sys
import json
from threading import Thread, Timer
import random
from importlib import import_module
import webbrowser

SCRIPTDIR = os.path.dirname(os.path.abspath(__file__))

print_ = print

def print(*argvs, **kwargs):
    print_(*argvs, **kwargs)

def make_path(*p):
    return os.path.join(SCRIPTDIR, *p)

class LanguageLoader:
    def __init__(self):
        self.load_lang()
    def load_lang(self, lname=None):
        if lname != None:
            self.lang_name = lname
        else:
            with open(make_path("language.txt")) as f:
                self.lang_name = f.read().replace("\n", "")
        if self.lang_name + ".json" in os.listdir(make_path("languages")):
            with open(make_path("languages", self.lang_name + ".json")) as f:
                lang = json.loads(f.read())
                self.lang = lang
        else:
            print("Language {} is not installed! Please change language.txt to installed language!".format(self.lang_name))
            if lname == None:
                self.load_lang("english")
                self.lang_name = "english"
            else:
                print("No language file found!")
                sys.exit(1)
    def get_lang(self):
        return self.lang

class Language:
    def __init__(self, data, name):
        self.NAME = name
        self.cmds = data["commands"]
        self.weather = data["weather_strings"]
        self.extensions = data["extensions_strings"]
        self.timer = data["timer_strings"]
        self.renamef = data["renamef_strings"]
        self.misslib = data["missing_lib_strings"]
        self.langswitch = data["lang_switch_strings"]

lang_loader = LanguageLoader()
lang_json = lang_loader.get_lang()
lang = Language(lang_json, lang_loader.lang_name)

with import_module("contextlib").redirect_stdout(None):
    try:
        from pygame import mixer
        def make_noise(rep=3):
            mixer.init()
            mixer.music.load(make_path("res", "beep_beep_beep.mp3"))
            mixer.music.play(rep)
    except ImportError:
        print(lang.misslib["pygame"])
        def make_noise(rep=3):
            print(lang.misslib["pygame"])
try:
    import requests
    def get_weather_city(city, key):
        r = requests.get("http://api.openweathermap.org/data/2.5/weather?q={0}&APPID={1}&units=metric".format(city, key))
        return r.json()
    def get_weather_loc(lat, lon, key):
        r = requests.get("http://api.openweathermap.org/data/2.5/weather?lat={0}&lon={1}&APPID={2}&units=metric".format(lat, lon, key))
        return r.json()
except ImportError:
    requests = False
    print(lang.misslib["requests"])
    def get_weather_city(city, key):
        print(lang.misslib["requests"])
        return None
    def get_weather_loc(city, key):
        print(lang.misslib["requests"])
        return None

class API:
    class Signal:
        def __init__(self, msg):
            self.msg = msg

def print_weather(data):
    if data != None:
        if "main" in data:
            print(lang.weather["desc"].format(data["weather"][0]["description"]))
            print("")
            f = data["main"]
            print(lang.weather["temp"].format(f["temp"]))
            print(lang.weather["humidity"].format(f["humidity"]))
            print(lang.weather["pressure"].format(f["pressure"]))
            print(lang.weather["wind"].format(data["wind"]["speed"]))
        elif "cod" in data:
            print(lang.weather["city_not_found"])
        else:
            print(lang.weather["invalid_data"])

class InputProcessor:
    def __init__(self, ext_load_text=True):
        self.testers = {
            (lambda self, txt: self.set_timeout if any([re.match(x, txt.lower()) for x in lang.cmds["set_timer"]]) else False),
            (lambda self, txt: self.rename_file if any([re.match(x, txt.lower()) for x in lang.cmds["rename_file"]]) else False),
            (lambda self, txt: self.exit if any([re.match(x, txt.lower()) for x in lang.cmds["exit"]]) else False),
            (lambda self, txt: self.get_weather_city if any([re.match(x, txt.lower()) for x in lang.cmds["weather_city"]]) else False),
            (lambda self, txt: self.get_weather_loc if any([re.match(x, txt.lower()) for x in lang.cmds["weather_loc"]]) else False),
            (lambda self, txt: self.web_browser if any([re.match(x, txt.lower()) for x in lang.cmds["web_browser"]]) else False),
            (lambda self, txt: self.lang_switch if any([re.match(x, txt.lower()) for x in lang.cmds["lang_switch"]]) else False)
        }
        self.cusomtesters = set()
        self.weather_api_key = "784a4692220a1da87669120fca562bcb"
        self.extensions_list = os.listdir(make_path("extensions"))
        self.load_extensions(ext_load_text)
    def __call__(self, txt):
        for tester in self.testers:
            res = tester(self, txt)
            if res != False:
                return res(txt)
        for (group, tester) in self.customtesters:
            res = tester(txt)
            if res != False:
                return res(txt)
    def load_extensions(self, out):
        self.customtesters = set()
        self.extensions = []
        for ext in self.extensions_list:
            if ext.endswith(".py"):
                self.extensions.append(import_module("extensions.{}".format((os.path.splitext(ext)[0] if "." in ext else ext))))
        for ext in self.extensions:
            try:
                ext.init(self.register_request, lang.NAME)
                if out: print(lang.extensions["loaded"].format(os.path.splitext(os.path.basename(ext.__file__))[0]))
            except AttributeError:
                if out: print(lang.extensions["no_init_function"].format(os.path.splitext(os.path.basename(ext.__file__))[0]))
    def register_request(self, request, group):
        self.customtesters.add((group, request))
    
    def set_timeout(self, txt):
        spl = txt.lower().split(" ")
        try:
            time = float(spl[-2])
        except ValueError:
            print(lang.timer["invalid_int"])
            time = None
        unit = spl[-1][0]
        if time != None:
            if unit == "s":
                Timer(time, make_noise).start()
                print(lang.timer["set"])
            elif unit == "m":
                Timer(time * 60, make_noise).start()
                print(lang.timer["set"])
            elif unit == "h":
                Timer(time * 60 * 60, make_noise).start()
                print(lang.timer["set"])
            else:
                print(lang.timer["invalid_unit"])
    def rename_file(self, txt):
        spl = txt.split(" ")
        if len(spl) == 4:
            name1 = spl[1]
            name2 = spl[3]
            try:
                os.rename(name1, name2)
            except OSError:
                print(lang.renamef["problem_rename"])
            else:
                print(lang.renamef["renamed"])
        else:
            print(lang.renamef["invalid_req"])
    def exit(self, txt):
        return API.Signal("ExitAssistant")
    def get_weather_city(self, txt):
        spl = txt.split(" ")
        if len(spl) >= 2:
            city = spl[-1]
            data = get_weather_city(city, self.weather_api_key)
            print_weather(data)
        else:
            print(lang.weather["invalid_req"])
    def get_weather_loc(self, txt):
        if requests:
            r = requests.get("http://ipinfo.io/loc")
            loc = r.text.replace("\n", "").split(",")
            data = get_weather_loc(loc[0], loc[1], self.weather_api_key)
            print_weather(data)
        else:
            print(lang.weather["no_requests_lib"])
    def web_browser(self, txt):
        Thread(target=webbrowser.open, args=("",)).start()
    def lang_switch(self, txt):
        global lang_loader
        global lang_json
        global lang
        spl = txt.split(" ")
        if len(spl) >= 2:
            with open(make_path("language.txt"), "w") as f:
                f.write(spl[1])
            lang_loader = LanguageLoader()
            lang_json = lang_loader.get_lang()
            lang = Language(lang_json, lang_loader.lang_name)
            self.__init__(False)
            print(lang.langswitch["switched"])

process_input = InputProcessor()

def main_loop():
    while True:
        try:
            inp = input(">>> ")
        except KeyboardInterrupt:
            pass
        except EOFError:
            print()
            break
        else:
            res = process_input(inp)
            if type(res) == API.Signal:
                if res.msg == "ExitAssistant":
                    break

if __name__ == "__main__":
    main_thread = Thread(target=main_loop)
    main_thread.start()
    main_thread.join()
