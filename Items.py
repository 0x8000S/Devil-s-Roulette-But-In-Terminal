# Author: 氢気氚
# Items.py
import time
import Var
import random
import colorama
colorama.init(autoreset=True)

# 自定义异常
class MagazineEmpty(Exception):
    pass

class HPZero(Exception):
	def __init__(self, p:"Player"):
		self.player = p

class BulletEmpty(Exception):
    pass

class Data:
	Level = 1
	DrinkBeer = 0
	UseItem = 0
	DamageTaken = 0
	Hit = 1
	PillsHit = 0
	BulletsFired = 0
	Lose = 0
	Round = 0
	PlunderedFunds = 0
	RoundHP = [2, 4, 6]
	Reload = False
	isGame = True
	Winner:"Player" = None
	@classmethod
	def Rest(cls):
		cls.Level = 1
		cls.DrinkBeer = 0
		cls.UseItem = 0
		cls.DamageTaken = 0
		cls.BulletsFired = 0
		cls.Hit = 1
		cls.PillsHit = 0
		cls.Lose = 0
		cls.Round = 0
		cls.PlunderedFunds = 0
		cls.RoundHP = [3, 4, 6]
		cls.Reload = False
		cls.isGame = True
		cls.Winner = None
	@classmethod
	def GetCurrentLevelHp(cls) -> int:
		return cls.RoundHP[cls.Level-1]

class Item:
	Name = "Item"
	def Exce(self, P:"PlayerGroup", G:"Gun"):
		p = P.GetCurrentPlayerObject()
		print(f"{p.GetName()}使用了{self.Name}")
		time.sleep(0.2)

class Beer(Item):
	Name = "Beer"
	def Exce(self, P, G) -> Var.BulletState:
		super().Exce(P, G)
		p = P.GetCurrentPlayerObject()
		shoot = G.Shoot()
		print(f"{p.GetName()}退掉了一颗{Var.BulletName[shoot]}")
		if P.GetCurrentPlayerObject().tag == Var.Tag.Player:
			Data.DrinkBeer += 500
		return None

class Hacksaw(Item):
	Name = "Hacksaw"
	def Exce(self, P, G):
		super().Exce(P, G)
		p = P.GetCurrentPlayerObject()
		Data.Hit += 1
		print(f"{p.GetName()}的伤害翻倍了!")

class Loupe(Item):
	Name = "Loupe"
	def Exce(self, P, G) -> Var.BulletState:
		super().Exce(P, G)
		p = P.GetCurrentPlayerObject()
		if p.tag == Var.Tag.Player:
			print(f"{p.GetName()}的下一颗子弹是{Var.BulletName[G.GetWillShootBulletObject()]}")
		return G.GetWillShootBulletObject()

class Cigarette(Item):
	Name = "Cigarette"
	def Exce(self, P, G):
		super().Exce(P, G)
		p = P.GetCurrentPlayerObject()
		p.BloodReturn()
		print(f"{p.GetName()}回复了一点血量,现在是{p.GetHp()}点血量")

class Manacles(Item):
	Name = "Manacles"
	def Exce(self, P, G):
		super().Exce(P, G)
		P.GetNextPlayerObject().manacles = True
		print(f"{P.GetNextPlayerObject().GetName()}暂停行动一次")

class Reversal(Item):
	Name = "Reversal"
	def Exce(self, P, G):
		super().Exce(P, G)
		if G.GetBulletList()[-1] == Var.BulletState.R:
			G.BulletList[-1] = Var.BulletState.B
		elif G.GetBulletList()[-1] == Var.BulletState.B:
			G.BulletList[-1] = Var.BulletState.R
		print("下一发子弹已被逆转")
		return G.GetWillShootBulletObject()

class ExpiredMedicines(Item):
	Name = "ExpiredMedicines"
	def Exce(self, P, G):
		super().Exce(P, G)
		p = P.GetCurrentPlayerObject()
		if random.random() <= 0.4:
			p.BloodReturn(2)
			print(f"还算幸运,{p.GetName()}回复了两点血量,{p.GetName()}现在还有{p.GetHp()}点血量")
		else:
			p.Hit(1)
			print(f"该死!{p.GetName()}受到了一点伤害,{p.GetName()}现在还有{p.GetHp()}点血量")

class DisposablePhone(Item):
	Name = "DisposablePhone"
	def Exce(self, P, G):
		super().Exce(P, G)
		p = P.GetCurrentPlayerObject()
		index = random.randint(0, len(G.GetBulletList())-1)
		if p.tag == Var.Tag.Player:
			print(f"第{len(G.GetBulletList())-index}颗子弹是{Var.BulletName[G.GetBulletList()[index]]}")
		return [len(G.GetBulletList())-index, G.GetBulletList()[index]]

class Gun:
	def __init__(self):
		self.BulletList = []
		self.Shooted = []
	def CreateBullet(self):
		Data.Reload = True
		self.BulletList = []
		round = [2, 3, 3][Data.Level-1]
		self.BulletList.extend([Var.BulletState.R, Var.BulletState.B])
		for i in range(round):
			self.BulletList.append(random.choice([Var.BulletState.R, Var.BulletState.B]))
		random.shuffle(self.BulletList)
	def Shoot(self) -> Var.BulletState:
		if len(self.GetBulletList()) <= 0:
			self.Shooted.clear()
			raise BulletEmpty
		Data.Reload = False
		shoot = self.BulletList[-1]
		self.Shooted.append(shoot)
		self.BulletList.pop()
		return shoot
	def GetWillShootBulletObject(self) -> Var.BulletState:
		return self.BulletList[-1]
	def GetBulletList(self) -> list[Var.BulletState]:
		return self.BulletList
	def Statistics(self, org=None) -> list[int]:
		if org == None:
			countPoint = self.BulletList
		else:
			countPoint = org
		R = 0
		B = 0
		for i in countPoint:
			if i == Var.BulletState.R:
				R += 1
			elif i == Var.BulletState.B:
				B += 1
		return [R, B]
	def Check(self):
		if len(self.GetBulletList()) <= 0:
			raise BulletEmpty

class StorageTable:
	def __init__(self, P:"PlayerGroup", G:Gun):
		self.Pack:list[Item] = []
		self.G = G
		self.P = P
	def AddItem(self, add_item:Item):
		if len(self.Pack) < 8:
			self.Pack.append(add_item)
		else:
			print(f"{colorama.Back.RED}背包已满,道具{add_item.Name}已弃置!")
	def UseItem(self, which:Item):
		if len(self.G.GetBulletList()) <= 0:
			raise BulletEmpty
		ret = which.Exce(self.P, self.G)
		self.Pack.remove(which)
		return ret
	def GetPackItems(self) -> list[Item]:
		return self.Pack
	def ClearPack(self):
		self.Pack.clear()
	def HasItem(self, findItem) -> bool:
		for i in self.Pack:
			if isinstance(i, findItem):
				return True
		return False
	def GetItem(self, findItem):
		for i in self.Pack:
			if isinstance(i, findItem):
				return i

class ListVariable:
	def __init__(self, var):
		self.value = var
	def get(self):
		return self.value
	def set(self, var):
		if isinstance(self.value, list):
			self.value.append(var)
		else:
			self.value = var
	def clear(self):
		if isinstance(self.value, list):
			self.value.clear()
		else:
			self.value = None
	def remove(self, x):
		if isinstance(self.value, list):
			self.value.remove(x)

class Ai:
	def __init__(self, p:"Player", P:"PlayerGroup", G:Gun):
		self.p = p
		self.P = P
		self.G = G
		self.PhonePos:ListVariable = ListVariable([])
		self.PhoneBul:ListVariable = ListVariable([])
		self.deep = 0
		self.NextBul:ListVariable = ListVariable(None)
		self.BehaviorTable = [
			(Loupe, lambda:self.NextBul.get() == None, [self.NextBul], 0.25),
			(DisposablePhone, lambda:random.random() <= 0.8, [self.PhonePos, self.PhoneBul], 0),
			(Reversal, lambda:self.NextBul.get() == Var.BulletState.B or random.random() >= 0.9, [], 0),
			(Beer, lambda:(self.NextBul.get() == None and random.random() < 0.65) or self.NextBul.get() == Var.BulletState.B, [self.NextBul], 0),
			(Cigarette, lambda:Data.GetCurrentLevelHp() > p.GetHp() and random.random() >= 0.1, [], 0),
			(ExpiredMedicines, lambda:self.p.GetPack().HasItem(Cigarette) == False or random.random() >= 0.45, [], 0),
			(Hacksaw, lambda:self.NextBul.get() == Var.BulletState.R or random.random() >= 0.6, None, 0.15),
			(Manacles, lambda:random.random() >= 0.3 or (len(self.G.GetBulletList()) <= 3 and random.random() <= 0.6), [], 0)
		]
	def CalculateProbability(self) -> float:
		stab = self.G.Statistics()
		if (stab[0] + stab[1]) == 0:
			raise BulletEmpty
		return stab[0] / (stab[0] + stab[1])
	def ClearPhoneIndex(self):
		self.PhonePos.clear()
		self.PhoneBul.clear()
		self.NextBul.clear()
	def CheckPhone(self, nextbul:Var.BulletState):
		pathP = []
		pathV = []
		ret = nextbul
		NowBulLen = len(self.G.GetBulletList())
		for pos, var in zip(self.PhonePos.get(), self.PhoneBul.get()):
			if NowBulLen == pos:
				ret = var
				pathP.append(pos)
				pathV.append(var)
		for pos, var in zip(pathP, pathV):
			self.PhonePos.remove(pos)
			self.PhoneBul.remove(var)
		return ret
	def AiItemsSelect(self, Probability:float) -> float:
		prob = Probability
		pack = self.p.GetPack()
		if prob == 1:
			self.NextBul.set(Var.BulletState.R)
		elif prob == 0:
			self.NextBul.set(Var.BulletState.B)
		self.NextBul.set(self.CheckPhone(self.NextBul.get()))
		if self.deep >= 3:
			self.deep = 0
			return prob
		for item, cond, eq, probv in self.BehaviorTable:
			if pack.HasItem(item):
				if cond():
					ret = pack.UseItem(pack.GetItem(item))
					self.NextBul.set(self.CheckPhone(self.NextBul.get()))
					if ret in Var.BulletState:
						if ret == Var.BulletState.R:
							prob += probv
						elif ret == Var.BulletState.B:
							prob -= probv
					if isinstance(item, Reversal):
						if self.NextBul.get() != None:
							self.NextBul.set(ret)
					if ret != None:
						if not isinstance(ret, list):
							ret = [ret]
						for i, v in zip(eq, ret):
							i.set(v)
					if isinstance(item, Beer):
						self.NextBul.clear()
					if eq == None:
						prob += prob
		if random.random() >= 0.2:
			self.deep += 1
			prob = self.AiItemsSelect(prob)
		self.deep = 0
		if self.NextBul.get() == Var.BulletState.R:
			prob = 1
		elif self.NextBul.get() == Var.BulletState.B:
			prob = 0
		return prob

class Player:
	def __init__(self, tags:Var.Tag, name:str, P:"PlayerGroup", G:Gun):
		self.tag = tags
		self.name = name
		self.manacles = False
		self.HP = Data.RoundHP[Data.Level-1]
		self.Again = False
		self.Pack = StorageTable(P, G)
		self.knife = False
		self.knifeTip = False
		self.AiPoint = Ai(self, P, G)
	def GetHp(self) -> int:
		return self.HP
	def GetName(self) -> str:
		return self.name
	def GetAiPoint(self) -> Ai:
		return self.AiPoint
	def Hit(self, hit=1) -> bool:
		Data.Hit = 1
		self.HP -= hit
		if self.knife:
			self.HP = 0
		if Data.Level == 3:
			if not self.knife:
				if self.GetHp() <= 2:
					self.FallKnife()
		if self.HP <= 0:
			raise HPZero(self) # 模块内自动抛出异常,避免层层检查
		return False
	def BloodReturn(self, value:int=1):
		self.HP += value
		if self.GetHp() >= Data.RoundHP[Data.Level-1]:
			self.HP = Data.RoundHP[Data.Level-1]
	def GetPack(self) -> StorageTable:
		return self.Pack
	def FallKnife(self):
		self.knife = True
		print(f"{self.name}的闸刀已落下,再挨一下就结束了")
		self.knifeTip = True
	def GetKnife(self) -> bool:
		return self.knife

class PlayerGroup:
	def __init__(self, G:Gun):
		self.PlayerList:list[Player] = []
		self.PlayerList.append(Player(Var.Tag.Player, "你", self, G))
		self.PlayerList.append(Player(Var.Tag.AI, "恶魔", self, G))
		self.Index = 0
		self.G = G
	def SetupLevel(self):
		self.SetPoint(0)
		self.ClearEveryonePack()
		hp = Data.RoundHP[Data.Level-1]
		for i in self.PlayerList:
			i.HP = hp
			i.manacles = False
	def SetPoint(self, point:int):
		self.Index = point
	def GetPointPlayer(self, index:int) -> Player:
		return self.PlayerList[index]
	def PushNextPlayer(self) -> Player:
		if Data.Reload == False:
			self.Index = (self.Index + 1) % len(self.PlayerList)
		return self.PlayerList[self.Index]
	def GetNextPlayerObject(self) -> Player:
		return self.PlayerList[(self.Index+1)%len(self.PlayerList)]
	def GetCurrentPlayerObject(self) -> Player:
		return self.PlayerList[self.Index]
	def GetGroup(self) -> list[Player]:
		return self.PlayerList
	def WhichDied(self) -> Player | None:
		for i in self.PlayerList:
			if i.GetHp() <= 0:
				return i
		return None
	def WhichWin(self) -> Player | None:
		for i in self.PlayerList:
			if i.GetHp() > 0:
				return i
		return None
	def GiveItems(self, p:Player, count=2):
		pack = p.GetPack()
		for i in range(count):
			items = random.choice(Item.__subclasses__())
			print(f"{p.GetName()}获得了一个{items.Name}")
			pack.AddItem(items())
			time.sleep(0.4)
	def GiveItemsEveryone(self, count=2):
		for i in self.PlayerList:
			self.GiveItems(i, count)
	def ClearEveryonePack(self):
		for i in self.PlayerList:
			i.GetPack().ClearPack()
