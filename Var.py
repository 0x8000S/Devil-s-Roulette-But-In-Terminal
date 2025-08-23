# Author: 氢気氚
# Var.py
from enum import Enum

class BulletState(Enum):
    R = 0
    B = 1

BulletName:dict[BulletState:str] = {
    BulletState.R: "实弹",
    BulletState.B: "空包弹"
}

class Tag(Enum):
    Player = 0
    AI = 1

class Scope(Enum):
    Self=0
    Counterpart = 1