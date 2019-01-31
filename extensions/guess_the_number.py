class Extension:
    re = __import__("re")
    random = __import__("random")
    def guess_the_number(txt):
        if txt.endswith("number"):
            low = 0
            high = 100
        elif txt.startswith("guess number"):
            rng = txt.split(" ", 2)[-1].strip(" ").split("-")
            try:
                low = int(rng[0])
                high = int(rng[1])
            except ValueError:
                print("Invalid range!")
                low = 0
                high = 100
        elif txt.startswith("guess the number"):
            rng = txt.split(" ", 3)[-1].strip(" ").split("-")
            try:
                low = int(rng[0])
                high = int(rng[1])
            except ValueError:
                print("Invalid range!")
                low = 0
                high = 100
        n = Extension.random.randint(low, high)
        print("Guess the number ({0} - {1})".format(low, high))
        print("")
        g = 0
        while True:
            try:
                guess = int(input("Your guess: "))
            except ValueError:
                print("Invalid input!")
                continue
            except KeyboardInterrupt:
                break
            except EOFError:
                break
            else:
                g += 1
                if guess > n:
                    print("Go lower!")
                elif guess < n:
                    print("Go higher!")
                elif guess == n:
                    print("")
                    print("You guessed the number with {} guesses!".format(g))
                    break

def init(register, language):
    reqs = (
        (lambda txt: Extension.guess_the_number if Extension.re.match(r"guess (the )?number( [0-9]+( )?\-( )?[0-9]+)?", txt.lower()) else False),
    )
    for req in reqs:
        register(req, "guess_the_number")
