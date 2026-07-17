class ColorRecognition:
    def __init__(self):
        self.black_threshold = 60
        self.black_eps = 14
        self.brown_threshold = 130
        self.brown_eps = 16
        self.white_threshold = 875
        self.white_eps = 26

    def find_color(self, ground):
        reflected = ground[0] + ground[1]
        if reflected < 2*(self.black_threshold + 2*self.black_eps) and reflected > 2*(self.black_threshold - 2*self.black_eps):
            return "black"
        elif reflected < 2*(self.brown_threshold + 2*self.brown_eps) and reflected > 2*(self.brown_threshold - 2*self.brown_eps):
            return "brown"
        elif reflected < 2*(self.white_threshold + 2*self.white_eps) and reflected > 2*(self.white_threshold - 2*self.white_eps):
            return "white"
        else:
            return "floor"