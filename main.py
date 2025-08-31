# Author: 氢気氚
# main.py
import random
import time
import Items
import Var
import colorama

colorama.init(autoreset=True)

class Win(Exception):
    def __init__(self, p:Items.Player):
        Items.Data.Winner = p

def SettlementWinner():
    wp = Items.Data.Winner.Data
    wp.PlunderedFunds = 1000000
    wp.PlunderedFunds += wp.UseItem * 1000
    wp.PlunderedFunds -= wp.DrinkBeer * 200
    wp.PlunderedFunds -= wp.Lose * 800
    wp.PlunderedFunds += wp.DamageTaken * 100
    wp.PlunderedFunds += wp.BulletsFired * 250
    wp.PlunderedFunds += wp.PillsHit * 20
    print(f"赢家:\t{Items.Data.Winner.GetName()}")
    print(f"存活回合数:\t{Items.Data.Round}")
    print(f"受击次数:\t{wp.Lose}")
    print(f"药片受伤:\t{wp.PillsHit}")
    print(f"使用道具数量:\t{wp.UseItem}")
    print(f"饮下的啤酒:\t{wp.DrinkBeer}ML")
    print(f"扣下的扳机:\t{wp.BulletsFired}")
    for i in range(1, wp.PlunderedFunds+1, 8):
        print(f"最终带走:\t${i}", end="\r")
    print(f"最终带走:\t${wp.PlunderedFunds}", end="\r")
    print("\n", end="")


def CheckManacles(p:Items.Player):
    if p.manacles:
        print(f"{p.GetName()}被镣铐锁住了")
        p.manacles = False
        return True
    return False

def BroadcastBullet(G:Items.Gun, P:Items.PlayerGroup):
    time.sleep(1)
    Count = G.Statistics()
    if Items.Data.Level == 2:
        P.GiveItemsEveryone()
    elif Items.Data.Level == 3:
        P.GiveItemsEveryone(4)
    if not P.WhichDied():
        print(f"{colorama.Back.BLACK}本次共有{Count[0]}颗实弹,{Count[1]}颗空包弹")

def CheckBullet(G:Items.Gun, P:Items.PlayerGroup):
    if len(G.GetBulletList()) <= 0:
        time.sleep(1)
        print("枪内子弹已射完,开始重新上膛")
        if P.GetPointPlayer(0).manacles == False:
            P.SetPoint(0)
        G.CreateBullet()
        for p in P.PlayerList:
            p.GetAiPoint().ClearPhoneIndex()
        BroadcastBullet(G, P)
        Items.Data.Round += 1

def CheckHp(P:Items.PlayerGroup, G:Items.Gun, died:Items.Player):
    if died.tag == Var.Tag.AI:
        if Items.Data.Level < 3:
            Items.Data.Level += 1
            print(f"{died.GetName()}死掉了,进入{Items.Data.Level}阶段")
            if Items.Data.Level >= 3:
                print(f"{colorama.Back.RED}上阶段的道具已清空")
            P.SetupLevel()
            G.CreateBullet()
            BroadcastBullet(G, P)
        elif Items.Data.Level == 3:
            raise Win(P.WhichWin()) # 异常,抛出! 随后异常会在while True主循环内捕获,非常好用
    elif died.tag == Var.Tag.Player:
        raise Win(P.WhichWin()) # 这个也是,这可以快速回到顶部


def ShowPlayerHUD(P:Items.PlayerGroup):
    p = P.GetCurrentPlayerObject()
    showText = f"{colorama.Back.RED}<S>向恶魔射击\t{colorama.Back.BLUE}<M>向自己射击\t"
    if Items.Data.Level > 1:
        showText += "<U>使用道具"
    print(f"恶魔血量:{colorama.Fore.RED}{"▮"*P.GetNextPlayerObject().GetHp()}")
    print(f"你的血量:{colorama.Fore.RED}{"▮"*p.GetHp()}")
    print(showText)

def ShowPlayerItems(p:Items.Player):
    index = 0
    for i in p.GetPack().GetPackItems():
        print(f"{colorama.Back.GREEN}[{index}]-{i.Name}", end="\t")
        if index % 4 == 0 and index != 0:
            print("\n", end="")
        index += 1
def EffectWholesale(p:Items.Player):
    while True:
        ShowPlayerItems(p)
        try:
            com = input("<B>返回\n")
            if com == "B":
                break
            com = int(com)
            WillUse = p.GetPack().GetPackItems()[com]
            p.GetPack().UseItem(WillUse)
        except (ValueError, IndexError, TypeError):
            print(f"{colorama.Back.RED}非法输入!")

def AssignmentPersonaField(mode:int, scope:Var.Scope, P:Items.PlayerGroup):
    P.GetCurrentPlayerObject().Data.BulletsFired += 1
    if mode == 0:
        print(f"你选择了{"向恶魔射击" if scope == Var.Scope.Counterpart else "向你自己射击"}")
    elif mode == 1:
        time.sleep(1)
        print(f"{P.GetCurrentPlayerObject().GetName()}选择了{f"向{P.GetNextPlayerObject().GetName()}射击" if scope == Var.Scope.Counterpart else "向它自己射击"}")

def JudgedHit(scope:Var.Scope, G:Items.Gun, P:Items.PlayerGroup, mode=0):
    G.Check()
    match scope:
        case Var.Scope.Counterpart:
            AssignmentPersonaField(mode, scope, P)
            if G.Shoot() == Var.BulletState.R:
                P.GetCurrentPlayerObject().Data.DamageTaken += Items.Data.Hit
                if mode == 0:
                    print(f"砰!{P.GetNextPlayerObject().GetName()}被{P.GetCurrentPlayerObject().GetName()}被射中了,造成了{Items.Data.Hit}点伤害")
                elif mode == 1:
                    time.sleep(1)
                    print(f"砰!{P.GetNextPlayerObject().GetName()}被{P.GetCurrentPlayerObject().GetName()}射中了,受到了{Items.Data.Hit}点伤害")
                P.GetNextPlayerObject().Data.Lose += 1
                P.GetNextPlayerObject().Hit(Items.Data.Hit)
            else:
                if mode == 0:
                    print(f"咔!{P.GetCurrentPlayerObject().GetName()}射出了一发空包弹")
                elif mode == 1:
                    time.sleep(1)
                    print(f"咔!{P.GetCurrentPlayerObject().GetName()}射出了一发空包弹")
        case Var.Scope.Self:
            AssignmentPersonaField(mode, scope, P)
            if G.Shoot() == Var.BulletState.R:
                P.GetCurrentPlayerObject().Data.DamageTaken += Items.Data.Hit
                if mode == 0:
                    print(f"砰!{P.GetCurrentPlayerObject().GetName()}射中了你自己,造成了{Items.Data.Hit}点伤害")
                elif mode == 1:
                    print(f"砰!{P.GetCurrentPlayerObject().GetName()}射中了它自己,造成了{Items.Data.Hit}点伤害")
                P.GetNextPlayerObject().Data.Lose += 1
                P.GetCurrentPlayerObject().Hit(Items.Data.Hit)
            else:
                if P.GetCurrentPlayerObject().Again != True:
                    P.GetCurrentPlayerObject().Again = True
                if mode == 0:
                    print(f"咔!{P.GetCurrentPlayerObject().GetName()}打出了一发空包弹")
                elif mode == 1:
                    print(f"咔!{P.GetCurrentPlayerObject().GetName()}射出了一发空包弹")
    Items.Data.Hit = 1
    G.Check()
    for p in P.PlayerList:
        p.GetAiPoint().NextBul.clear()

def AiThinksFlow(P:Items.PlayerGroup, G:Items.Gun):
    p = P.GetCurrentPlayerObject()
    ai = p.GetAiPoint()
    if CheckManacles(p):
        return
    if P.GetCurrentPlayerObject().Again:
        P.GetCurrentPlayerObject().Again = False
    time.sleep(random.randint(1,2))
    print(f"====->{p.GetName()}")
    prob = ai.CalculateProbability()
    prob = ai.AiItemsSelect(prob)
    if random.random() < prob:
        JudgedHit(Var.Scope.Counterpart, G, P, 1)
    else:
        JudgedHit(Var.Scope.Self, G, P, 1)
    if P.GetCurrentPlayerObject().Again:
        AiThinksFlow(P, G)

def PlayerFlow(P:Items.PlayerGroup, G:Items.Gun):
    if CheckManacles(P.GetCurrentPlayerObject()):
        _ = input("回车确认>")
        return
    if P.GetCurrentPlayerObject().Again:
        P.GetCurrentPlayerObject().Again = False
    while True:
        ShowPlayerHUD(P)
        com = input()
        match com:
            case "S":
                JudgedHit(Var.Scope.Counterpart, G, P)
                break
            case "M":
                JudgedHit(Var.Scope.Self, G, P)
                break
            case "U":
                if Items.Data.Level > 1:
                    EffectWholesale(P.GetCurrentPlayerObject())
                else:
                    print(f"{colorama.Back.RED}非法输入")
            
    if P.GetCurrentPlayerObject().Again:
        PlayerFlow(P, G)

def MainLoop(mode:int=0):
    Items.Data.Rest()
    G = Items.Gun()
    P = Items.PlayerGroup(G, mode)
    G.CreateBullet()
    BroadcastBullet(G, P)
    while True:
        try:
            if P.GetCurrentPlayerObject().tag == Var.Tag.Player:
                PlayerFlow(P, G)
            else:
                AiThinksFlow(P, G)
            G.Check()
            P.PushNextPlayer()
        except Exception as e: # 异常捕获机制,避免层层return
            try:
                print("====")
                raise e
            except Win as win:
                SettlementWinner()
                break
            except Items.HPZero as e:
                try:
                    CheckHp(P, G, e.player)
                except Win:
                    SettlementWinner()
                    break
                continue
            except Items.BulletEmpty:
                CheckBullet(G, P)
                continue
        finally:
            print("====")

def main():
    while True:
        print("===Devil's Roulette But In Terminal===")
        print(f"{colorama.Back.BLUE}[S]开始\t{colorama.Back.GREEN}[A]Ai Fight\t{colorama.Back.RED}[Q]退出")
        com = input()
        match com:
            case 'S':
                MainLoop(0)
            case 'A':
                MainLoop(1)
            case 'Q':
                break
if __name__ == "__main__":
    main()