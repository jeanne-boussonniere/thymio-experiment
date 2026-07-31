class ColorRecognition:
    PATCHES = [
        {"index": 0, "average": 60, "eps": 14, "name": "black"},  
        {"index": 1, "average": 903, "eps": 11, "name": "white"},  
        {"index": 2, "average": 145, "eps": 24, "name": "brown"}   
    ]

    def find_color(self, ground):
        reflected = ground[0] + ground[1]
        for i in range(3):
            if reflected < 2*(self.PATCHES[i]["average"] + 2*self.PATCHES[i]["eps"]) and reflected > 2*(self.PATCHES[i]["average"] - 2*self.PATCHES[i]["eps"]):
                return i,self.PATCHES[i]["name"]
        return -1,"floor"