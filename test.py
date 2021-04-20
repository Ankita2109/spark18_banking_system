class abc() :
    def __init__(self):
        print("Initialized")
        self.x = 5

    def func1(self):
        print("func 1")

    def func2(self):
        print("func2")
        self.func1()


if __name__ == "__main__":
    a = abc()
    print(a.x)
    a.func2()
