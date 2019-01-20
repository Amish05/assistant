import os
import re
from threading import Thread, Timer
import random
from importlib import import_module
import webbrowser
with import_module("contextlib").redirect_stdout(None):
    try:
        from pygame import mixer
        def make_noise(rep=3):
            mixer.init()
            mixer.music.load(make_path("res", "beep_beep_beep.mp3"))
            mixer.music.play(rep)
    except ImportError:
        print("Please install pygame library for timers to work!")
        def make_noise(rep=3):
            print("Please install pygame library for timers to work!")
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
    print("Please install requests library for weather info to work!")
    def get_weather_city(city, key):
        print("Please install requests library for weather info to work!")
        return None
    def get_weather_loc(city, key):
        print("Please install requests library for weather info to work!")
        return None

SCRIPTDIR = os.path.dirname(os.path.abspath(__file__))

def print_weather(data):
    if data != None:
        if data["main"]:
            print("Description: {}\n".format(data["weather"][0]["description"]))
            f = data["main"]
            print("Temperature: {}".format(f["temp"]))
            print("Humidity: {}%".format(f["humidity"]))
            print("Pressure: {} hPa".format(f["pressure"]))
            print("Wind: {} m/s".format(data["wind"]["speed"]))
        else:
            print("Invalid data from server!")

def make_path(*p):
    return os.path.join(SCRIPTDIR, *p)

class API:
    class Signal:
        def __init__(self, msg):
            self.msg = msg

class InputProcessor:
    def __init__(self):
        self.testers = {
            (lambda self, txt: self.set_timeout if re.match("(set )?timer(to )? [0-9]+ .+", txt.lower()) or re.match("(set )?timeout(to )? [0-9]+ .+", txt.lower()) else False),
            (lambda self, txt: self.rename_file if re.match("rename .+ to .+", txt) else False),
            (lambda self, txt: self.exit if txt.lower() in ("exit", "quit", "stop") else False),
            (lambda self, txt: self.say if txt.lower().startswith("say") else False),
            (lambda self, txt: self.get_weather_city if re.match("(what is )?(the )?weather (in )?.+", txt.lower()) else False),
            (lambda self, txt: self.get_weather_loc if re.match("(what is )?(the )?weather", txt.lower()) else False),
            (lambda self, txt: self.web_browser if re.match("(open )?(web )?browser", txt.lower()) else False),
            (lambda self, txt: self.extension_manager if re.match("extension(s)? [a-z]+", txt.lower()) else False)
        }
        self.weather_api_key = "784a4692220a1da87669120fca562bcb"
        self.extensions_list = os.listdir(make_path("extensions"))
        self.load_extensions(True)
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
                ext.init(self.register_request)
                if out: print("Loaded extension {}!".format(os.path.splitext(os.path.basename(ext.__file__))[0]))
            except AttributeError:
                if out: print("Extension {} doesn't contain init function!".format(os.path.splitext(os.path.basename(ext.__file__))[0]))
    def register_request(self, request, group):
        self.customtesters.add((group, request))
    
    def set_timeout(self, txt):
        spl = txt.lower().split(" ")
        try:
            time = float(spl[-2])
        except ValueError:
            print("Invalid time integer!")
            time = None
        unit = spl[-1][0]
        if time != None:
            if unit == "s":
                Timer(time, make_noise).start()
                print("Timeout set!")
            elif unit == "m":
                Timer(time * 60, make_noise).start()
                print("Timeout set!")
            elif unit == "h":
                Timer(time * 60 * 60, make_noise).start()
                print("Timeout set!")
            else:
                print("Invalid time unit!")
    def rename_file(self, txt):
        spl = txt.split(" ")
        if len(spl) == 4:
            name1 = spl[1]
            name2 = spl[3]
            try:
                os.rename(name1, name2)
            except OSError:
                print("Problem occured with renaming file/folder!")
            else:
                print("File/folder renamed!")
        else:
            print("Invalid rename file/folder request!")
    def exit(self, txt):
        return API.Signal("ExitAssistant")
    def say(self, txt):
        spl = txt.split(" ", 1)
        if len(spl) == 2:
            print(spl[1])
    def get_weather_city(self, txt):
        spl = txt.split(" ")
        if len(spl) >= 2:
            city = spl[-1]
            data = get_weather_city(city, self.weather_api_key)
            print_weather(data)
        else:
            print("Invalid weather request!")
    def get_weather_loc(self, txt):
        if requests:
            r = requests.get("http://ipinfo.io/loc")
            loc = r.text.replace("\n", "").split(",")
            data = get_weather_loc(loc[0], loc[1], self.weather_api_key)
            print_weather(data)
        else:
            print("Please install requests library for weather info to work!")
    def web_browser(self, txt):
        Thread(target=webbrowser.open, args=("",)).start()
    def extension_manager(self, txt):
        spl = txt.split(" ")
        cmd = spl[1]
        if cmd == "disable":
            if len(spl) >= 3:
                rem = True
                while rem:
                    rem = False
                    for req in self.customtesters:
                        if req[0] == spl[2]:
                            self.customtesters.remove(req)
                            rem = True
                            break
                print("Disabled command group {}!".format(spl[2]))
            else:
                self.customtesters = set()
                print("Disabled all extensions!")
        elif cmd == "enable":
            self.load_extensions(False)
            print("Enabled all extensions!")

process_input = InputProcessor()

def main_loop():
    while True:
        try:
            inp = input(">>> ")
        except KeyboardInterrupt:
            print()
            break
        except EOFError:
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
