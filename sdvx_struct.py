# 六维图
class Radar:
    def __init__(self):
        self.notes : int = 0
        self.peak : int = 0
        self.tsumami : int = 0
        self.tricky : int = 0
        self.hand_trip : int = 0
        self.one_hand : int = 0
        
    def __str__(self):
        return (f"Radar(notes={self.notes}, peak={self.peak}, "
                f"tsumami={self.tsumami}, tricky={self.tricky}, "
                f"hand_trip={self.hand_trip}, one_hand={self.one_hand})")

    def __repr__(self):
        return self.__str__()
    
# Novice(nov)
# Advanced(adv)
# Exhaust(exh)
# Infinite(inf)
# Gravity(grv)
# Heavenly(hvn)
# Vivid(vvd)
# Exceed(xcd)
# Maximum(mxm)
class Difficulty:
    def __init__(self):
        self.level : int = 0
        self.illustrator : str = None
        self.effected_by : str = None
        self.max_exscore : int = None
        self.radar : Radar = Radar()
        
    def __str__(self):
        return (f"Difficulty(level={self.level}, illustrator={self.illustrator}, "
                f"effected_by={self.effected_by}, max_exscore={self.max_exscore}, "
                f"radar={self.radar})")

    def __repr__(self):
        return self.__str__()
    
class SDVXStrcut:
    def __init__(self):
        self.id : str = None
        self.title : str = None
        self.title_yomigana : str = None
        self.artist : str = None
        self.artist_yomigana : str = None
        self.ascii : str = None
        self.bpm_max : int = None
        self.bpm_min : int = None
        self.date : int = None # 年月日
        # 1是Booth
        # 2是Infinite(inf)
        # 3是Gravity(grv)
        # 4是Heavenly(hvn)
        # 5是Vivid(vvd)
        # 6是Exceed(xcd)
        self.version : int = 0
        self.inf_ver : int = 0 # 第4个难度的版本(0为没有)
        self.diff_list : list[str] = []
        self.diffs : dict[str, Difficulty] = {}
        
    def __str__(self):
        diff_list_str = ', '.join(str(diff) for diff in self.diff_list)
        diffs_str = ', '.join(f"{key}: {value}" for key, value in self.diffs.items())
        
        return (f"SDVXStrcut(id={self.id}, title={self.title}, "
                f"title_yomigana={self.title_yomigana}, artist={self.artist}, "
                f"artist_yomigana={self.artist_yomigana}, ascii={self.ascii}, "
                f"bpm_max={self.bpm_max}, bpm_min={self.bpm_min}, "
                f"date={self.date}, version={self.version}, inf_ver={self.inf_ver}, "
                f"diff_list=[{diff_list_str}], diffs={{ {diffs_str} }})")

    def __repr__(self):
        return self.__str__()
    