class ColorRecognition:
    PATCHES = [
        {"index": 0, "average": 60, "eps": 14, "name": "black"},  
        {"index": 1, "average": 903, "eps": 11, "name": "white"},  
        {"index": 2, "average": 145, "eps": 24, "name": "brown"}   
    ]

    def __init__(self):
        self.current_patch = -1
        self.current_color = "floor"
        self.candidate = -1
        self.count = 0

    def find_color(self, ground):
        reflected = ground[0] + ground[1]
        for i in range(3):
            if reflected < 2*(self.PATCHES[i]["average"] + 2*self.PATCHES[i]["eps"]) and reflected > 2*(self.PATCHES[i]["average"] - 2*self.PATCHES[i]["eps"]):
                return i,self.PATCHES[i]["name"]
        return -1,"floor"

    def filtered_color(self,ground):
        patch, name = self.find_color(ground)
        if patch == self.candidate:
            self.count += 1
        else:
            self.candidate = patch
            self.count = 1
        if self.count >= 3:
            self.current_patch = patch
            self.current_color = name
        return self.current_patch, self.current_color