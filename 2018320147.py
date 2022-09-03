# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'FirstAgent', second = 'SecondAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    self.flag=0    #이 flag는 agent의 상태를 구분하기 위해 쓰입니다
    self.flag2=0 #이 flag는 우리 pacman이 food를 모두 먹었을때 양수로 설정됩니다
    '''
    Your initialization code goes here, if you need any.
    '''
  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)   #가능한 action들을 가져옵니다

    '''
    You should change this in your own agent.
    '''
    values = [self.evaluate(gameState, a) for a in actions]   #evaluate함수를 통해 values 리스트를 가져옵니다
    maxValue = max(values)   #가장 큰 value를 계산합니다
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]  #가장 value값이 높은 action을 저장합니다
    
    return random.choice(bestActions)    #bestaction중에 랜덤으로 선택합니다
  
  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)   #successor를 가져옵니다
    return successor
  
  def evaluate(self, gameState, action):
    features = self.getFeatures(gameState, action)   #feature를 가져옵니다
    weights = self.getWeights(gameState, action)   #weight를 가져옵니다
    return features * weights   #feature와 weight의 linear combination값을 계산하고 리턴합니다

#your_best
#baseline3와 거의 비슷한데 작은 오류들을 살짝 더 수정했습니다
#첫번째로 flag2라는 변수를 만듦으로써 우리 pacman이 모든 음식들을 먹었을때 본진으로 잘 돌아오게 만들었습니다
#그리고 주변에 적이 있을때 피하지만 적이 없어지면 pacman이 본진으로 돌아가지 않고 다시 food를 먹게끔 만들었습니다

class FirstAgent(DummyAgent):
 
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList2=self.getFood(gameState).asList()  #현재 food의 리스트를 가져옵니다
    foodList = self.getFood(successor).asList()     #다음 상태의 food리스트를 가져옵니다
    features['successorScore'] = -len(foodList)  #foodList의 길이로 해당 feature를 계산합니다
    features['onOffense'] = 0   #onOffense는 현재 공격상태인가를 나타냅니다
    features['attackerDistance'] = 0 #우리 pacman과 상대팀 적과의 거리
    features['redistanceToCapsule'] = 0 #파워캡슐의 거리와 반비례

    mynowState = gameState.getAgentState(self.index)
    if not mynowState.isPacman: self.flag=0 #우리 pacman이 진영으로 돌아오면 flag 다시 0으로 설정

    if len(foodList) >= 0: 
      if len(foodList) ==0 and self.flag2==0: #다음 상태에서 음식을 모두 먹을 경우
        self.flag2=1 #flag2를 1로 설정합니다
      elif self.flag2==0 :  #음식이 아직 남은 경우
       myPos = successor.getAgentState(self.index).getPosition() #다음상태의 위치
       minDistance = min([self.getMazeDistance(myPos, food) for food in foodList]) #다음상태의 food와 agent의 거리 최소값을 계산
       features['distanceToFood'] = minDistance  #그 거리를 해당 feature에 저장
    
    if self.flag==1: #flag가 1인경우, 즉 food를 먹은 경우 즉시 본진으로 돌아가게 했습니다
      foodList3=self.getFoodYouAreDefending(successor).asList() #우리편의 food
      myPos = successor.getAgentState(self.index).getPosition() #다음상태의 위치
      minDistance3 = min([self.getMazeDistance(myPos, food) for food in foodList3]) #다음상태 agent의 위치와 우리 food의 최소거리 계산
      features['distanceToFood'] = minDistance3
      #그 거리를 해당 feature에 저장(agent가 상대팀에서 food를 먹자마자 우리쪽으로 돌아오게 하기위해 우리팀의 food를 목적지로 설정한 것입니다)

      myState = successor.getAgentState(self.index) #다음 상태
      if myState.isPacman: features['onOffense'] = 1 #다음 상태에서 우리 agent가 아직 본진으로 돌아오지 못한 경우(pacman인 경우)
      else : 
        features['onOffense'] = 0 #본진으로 돌아오면 해당 feature를 0으로 놓았습니다
    
    capsuleList=self.getCapsules(gameState) #현재 파워캡슐 리스트 가져옴
    capsuleListNext=self.getCapsules(successor) #다음상태 파워캡슐 리스트 가져옴

    #food를 먹은 경우, 그리고 그것이 파워캡슐이 아닌경우, 혹은 음식을 모두 먹은경우 flag를 1로 설정(파워캡슐이면 무적이므로 본진으로 돌아갈 필요가 없습니다)
    if((len(foodList)!=len(foodList2) and self.flag!=2) or self.flag2==2):
      self.flag=1
    
    if(self.flag2==1): self.flag2=2 #flag2가 1인경우, 즉 다음턴에 food를 모두 먹은경우 flag2를 2로 설정
    #(이렇게 하는 이유는 음식을 모두 먹은 후에 본진으로 돌아가게 하기 위해서입니다)

    myStatetwo = successor.getAgentState(self.index) #다음상태
    myPostwo = myStatetwo.getPosition() #다음 agent의 위치
    if myStatetwo.isPacman:       #내가 공격중이고 상대방도 자기 진영에 있을때 거리가 너무 가까우면 피하는 방식
      enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)] #적들
      attackers = [a for a in enemies if ((not a.isPacman) and (a.getPosition() != None) and (a.scaredTimer<=2))] 
      #적들중에 자기 본진에 있는 경우 리스트에 저장, 적이 겁에 질린경우 피하지 않아도됨
      if len(attackers) > 0:
       dists = [self.getMazeDistance(myPostwo, a.getPosition()) for a in attackers] #자기 본진에 있는 적과 우리 pacman의 거리계산
       mindists=min(dists) #최소거리 저장
       features['attackerDistance'] = 4*(3/float(mindists)) #적과의 가까울경우 웬만하면 피하려함
       if mindists==1 : features['attackerDistance']=100 #적과의 거리가 1인경우 거의 무조건 피하려고함
       if myPostwo==mynowState.getPosition() : features['isSame']=1 #우리 agent는 가만히 있으면 안됨(적한테 먹힐 확률이 높으므로)
       if(mindists<=3 and self.flag==2) : self.flag=1 
       #파워캡슐을 얼마전에 먹었는데 강한 적이 근접하다면 무적인 상태가 끝났다고 판단하고 후퇴(baseline3에서 약간 수정) 

    if len(capsuleList) > 0: #파워캡슐이 있을경우
      mincapDistance = min([self.getMazeDistance(myPostwo, capsule) for capsule in capsuleList]) #다음 agent의 위치와 캡슐의 최소거리 계산
      features['redistanceToCapsule'] = 5*(4/(float(mincapDistance)+1)) #캡슐과 가까울수록 해당 feature에 큰 값 부여
      if(len(capsuleList)!=len(capsuleListNext)): #캡슐을 먹은경우
       features['redistanceToCapsule'] = 90 #해당 feature에 큰 값 부여
       self.flag=2 #flag 2로 설정(무적)

    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 20, 'distanceToFood': -1, 'onOffense':-100000, 'attackerDistance':-1, 'redistanceToCapsule':1, 'isSame' : -1000}
     #feature들의 weight값, food를 먹었을때 보상을 전보다 줄임



class SecondAgent(DummyAgent):

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition() #다음 위치
    mynowState = gameState.getAgentState(self.index)
    mynowPos = mynowState.getPosition() #현재 위치

    #해당 agent의 위치가 우리쪽인지 상대쪽인지 보고 해당 feature값을 결정합니다
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)] #적들의 리스트
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None] #적이 우리 쪽에 있는경우
    features['numInvaders'] = len(invaders) #우리쪽에 있는 적의 숫자
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders] #해당 agent와 적의 거리계산
      features['invaderDistance'] = min(dists) #가장 가까운 적과의 거리를 해당 feature에 저장
    elif len(invaders)==0: #현재 적이 우리 진영에 없는 경우
      if myPos==mynowPos : features['isSame']=1 #위치가 같은 경우 feature에 값 부여(무조건 움직이게 하는 방식)
      foodList3=self.getFoodYouAreDefending(successor).asList() #우리의 음식
      minDistance3 = min([self.getMazeDistance(myPos, food) for food in foodList3]) #해당 agent와 우리 음식의 최소거리 계산
      features['distanceToFood'] = minDistance3
      #그 최소 거리 저장(이 방식은 우리 agent가 maze의 깊은 곳에 있을때 음식 주변까지 나오게 해주는 역할을 합니다)

    return features

  def getWeights(self, gameState, action):
    return {'isSame' : -1000, 'numInvaders': -1000, 'onDefense': 2000, 'invaderDistance': -10, 'distanceToFood':-1}
    #feature 값들, onDefense값을 더욱 높임으로써 웬만하면 본진에 머무르게 했습니다, 적의 침공 전에 같은 곳에 머무르지 않게 했습니다