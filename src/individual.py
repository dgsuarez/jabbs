import base

class Individual(base.IndividualBot):
    
    def controller(self):
        return [(r".*", self.test)]

    def test(self, message):
        return "hola"
    test=simple(test)


if __name__ == "__main__":
    b = Individual("botiboti@127.0.0.1", "b3rb3r3ch0").start()
