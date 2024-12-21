from colors import Colors

class Themes:
    def __init__(self):
        self.themes = []
        self._add_themes()
        self.idx = 0
        self.theme = self.themes[self.idx]

    def change_theme(self):
        self.idx += 1
        self.idx %=  len(self.themes)
        self.theme = self.themes[self.idx]
        
    def _add_themes(self):
        brown = Colors((236, 218, 185), (178, 138, 104), (170,162,86), (207,209,134), (138,151,111), (107, 111, 70))
        green = Colors((234, 235, 200), (119, 154, 88), (244, 247, 116), (172, 195, 51), (138,151,111), (138,151,111))  
        blue = Colors((229, 228, 200), (60, 95, 135), (123, 187, 227), (43, 119, 191), (138,151,111), (138,151,111))
        gray = Colors((120, 119, 118), (86, 85, 84), (99, 126, 143), (82, 102, 128), (138,151,111), (138,151,111))

        self.themes = [brown, green,  blue, gray]