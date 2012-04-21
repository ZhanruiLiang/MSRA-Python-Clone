
class Instruction:
    def __init__(self, sender, rawstr):
        args = rawstr.split()
        cmd, sec = args[:2]
        args = args[2:]
        self.cmd = cmd
        self.sec = int(sec)
        self.args = args
        self.faction = sender.faction
        self.rawstr = rawstr

    def __repr__(self):
        return self.rawstr

