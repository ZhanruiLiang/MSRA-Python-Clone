
class Instruction:
    def __init__(self, rawstr):
        args = rawstr.split()
        cmd, sec = args[:2]
        args = args[2:]
        self.cmd = cmd
        self.sec = sec
        self.args = args

