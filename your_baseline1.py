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
    self.flag=0            #이 flag는 agent의 상태를 구분하기 위해 쓰입니다

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
    maxValue = max(values)  #가장 큰 value를 계산합니다
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]  #가장 value값이 높은 action을 저장합니다

    return random.choice(bestActions)   #bestaction중에 랜덤으로 선택합니다
  
  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)    #successor를 가져옵니다
    return successor
  
  def evaluate(self, gameState, action):
    features = self.getFeatures(gameState, action)   #feature를 가져옵니다
    weights = self.getWeights(gameState, action)   #weight를 가져옵니다
    return features * weights   #feature와 weight의 linear combination값을 계산하고 리턴합니다
    
#baseline1
#큰 형식은 기존 baseline과 비슷합니다
#offender는 점수 하나를 먹을때마다 본진으로 돌아가 점수를 취합니다
#defender는 기존 코드와 비슷하나 디펜더 역할에 충실하기 위해 되도록이면 본진을 벗어나지 않게끔 설계했습니다
class FirstAgent(DummyAgent):
 
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList2=self.getFood(gameState).asList()   #현재 food의 리스트를 가져옵니다
    foodList = self.getFood(successor).asList()    #다음 상태의 food리스트를 가져옵니다
    features['successorScore'] = -len(foodList)   #foodList의 길이로 해당 feature를 계산합니다
    features['onOffense'] = 0   #onOffense는 현재 공격상태인가를 나타냅니다

    if len(foodList) > 0: 
      myPos = successor.getAgentState(self.index).getPosition()  #다음상태의 위치
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList]) #다음상태의 food와 agent의 거리 최소값을 계산
      features['distanceToFood'] = minDistance #그 거리를 해당 feature에 저장
    
    if self.flag==1:    #flag가 1인경우, 즉 food를 먹은 경우 즉시 본진으로 돌아가게 했습니다
      foodList3=self.getFoodYouAreDefending(successor).asList()   #우리편의 food
      myPos = successor.getAgentState(self.index).getPosition()  #다음상태의 위치
      minDistance3 = min([self.getMazeDistance(myPos, food) for food in foodList3])  #다음상태 agent의 위치와 우리 food의 최소거리 계산
      features['distanceToFood'] = minDistance3   
      #그 거리를 해당 feature에 저장(agent가 상대팀에서 food를 먹자마자 우리쪽으로 돌아오게 하기위해 우리팀의 food를 목적지로 설정한 것입니다)

      myState = successor.getAgentState(self.index)   #다음 상태
      if myState.isPacman: features['onOffense'] = 1  #다음 상태에서 우리 agent가 아직 본진으로 돌아오지 못한 경우(pacman인 경우) 
      else : 
        features['onOffense'] = 0   #본진으로 돌아오면 해당 feature를 0으로 놓고 flag도 0으로 다시 설정했습니다
        self.flag=0

    if(len(foodList)!=len(foodList2)):   #food를 먹은 경우 flag를 1로 설정
      self.flag=1
      
    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1, 'onOffense':-100000}   #feature들의 weight값

  

class SecondAgent(DummyAgent):

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    #해당 agent의 위치가 우리쪽인지 상대쪽인지 보고 해당 feature값을 결정합니다
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]  #적들의 리스트
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]   #적이 우리 쪽에 있는경우
    features['numInvaders'] = len(invaders)    #우리쪽에 있는 적의 숫자
    if len(invaders) > 0:   
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]   #해당 agent와 적의 거리계산
      features['invaderDistance'] = min(dists)   #가장 가까운 적과의 거리를 해당 feature에 저장

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 600, 'invaderDistance': -10}   
    #feature 값들, onDefense값을 높임으로써 웬만하면 본진에 머무르게 했습니다