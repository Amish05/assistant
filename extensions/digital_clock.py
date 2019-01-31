class Extension:
    re = __import__("re")
    thr = __import__("threading")
    def digital_clock(txt):
        def inner():
            from tkinter import Tk, Label, BOTH
            import time
            root = Tk()
            root.title("Clock")
            clock = Label(root, font=('times', 30, 'bold'), bg='green')
            clock.pack(fill=BOTH, expand=1)
            def tick():
                timetext = time.strftime('%H:%M:%S')
                clock.config(text=timetext)
                clock.after(200, tick)
            tick()
            root.mainloop()
        Extension.thr.Thread(target=inner).start()

def init(register, language):
    reqs = (
        (lambda txt: Extension.digital_clock if Extension.re.match("(digital )?clock", txt.lower()) else False),
    )
    for req in reqs:
        register(req, "digital_clock")
