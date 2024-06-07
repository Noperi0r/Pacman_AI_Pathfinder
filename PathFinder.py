from pyamaze import maze, agent
from queue import PriorityQueue
from collections import deque

class PathFinder:
    def __init__(self):
        pass
    
    # Heuristic based on manhattan distance 
    def Heuristic(self, cell1, cell2): 
        x1, y1 = cell1
        x2, y2 = cell2
        
        return abs(x1 - x2) + abs(y1 - y2) 
    
    def AStarTest(self, m: maze):
        start = (m.rows, m.cols) # TODO: 플레이어 위치 받아오기 row col 
        goal = (1,1) # TODO: 플레이어 기준 가장 가까운 먹이 위치 받아오기
        
        gScore = {cell:float('inf') for cell in m.grid } # gScore: Distance passed 
        # TODO: 모든 cell 가져와서 row,col 저장
        gScore[start] = 0
        
        fScore = {cell:float('inf') for cell in m.grid } # fScore: Heuristic + gScore 
        fScore[start] = self.Heuristic(start, goal) # Start cell ~ Goal Cell  TODO: change 1,1 
        
        open = PriorityQueue()
        open.put((self.Heuristic(start, goal)+0, self.Heuristic(start, goal), start)) # f / heuristic / cell value  
        
        aPath = {}
        while not open.empty():
            currentCell = open.get()[2] # Get minimum value based on f > h > cell value
            if currentCell == goal:
                break
            
            for d in "ESNW":
                if m.maze_map[currentCell][d] == True: # (1, 1): {'E': 0, 'W': 0, 'N': 0, 'S': 1}, (2, 1): {'E': 1, 'W': 0, 'N': 1, 'S': 0}, ... 
                    childCellElement = [0,0]
                    if d == 'E':
                        childCellElement[0] = currentCell[0]
                        childCellElement[1] = currentCell[1]+1
                    if d == 'W':
                        childCellElement[0] = currentCell[0]
                        childCellElement[1] = currentCell[1]-1
                    if d == 'N':
                        childCellElement[0] = currentCell[0]-1
                        childCellElement[1] = currentCell[1]
                    if d == 'S':
                        childCellElement[0] = currentCell[0]+1
                        childCellElement[1] = currentCell[1]
                    
                    childCell = (childCellElement[0], childCellElement[1])
                    tempGScore = gScore[currentCell] + 1
                    tempFScore = tempGScore + self.Heuristic(childCell, goal)

                    if tempFScore < fScore[childCell]:
                        gScore[childCell] = tempGScore
                        fScore[childCell] = tempFScore
                        open.put((tempFScore, self.Heuristic(childCell, goal), childCell))
                        aPath[childCell] = currentCell
        
        fwdPath = {}
        cell = goal # Starting from goal cell  
        while cell != start:
            fwdPath[aPath[cell]] = cell # value of the forward path will be the key of the a path 
            cell = aPath[cell] # Next cell 
        return fwdPath
    
    def AStar(self, cellData):
        startPos = self.GetPlayerCellPos() # row, col 
        goalPos = self.GetNearestFoodCellPos()
        
        g_score = {cellPos:float('inf') for cellRow in cellData for cellPos in cellRow['grid']}
        g_score[startPos] = 0

        f_score = {cellPos:float('inf') for cellRow in cellData for cellPos in cellRow['grid']}
        f_score[startPos] = self.Heuristic(startPos, goalPos)
        
        open = PriorityQueue()
        open.put((self.Heuristic(startPos, goalPos)+0, self.Heuristic(startPos, goalPos), startPos)) # f / heuristic / cell value  
        
        aPath = {}
        while not open.empty():
            currentCellPos = open.get()[2]
            if currentCellPos == goalPos:
                break
            
            if cellData[startPos[0]][startPos[1]]['is_wall'] == False:
                for d in "ESNW":
                    childCellElement = [0,0]
                    if d == 'E':
                        childCellElement[0] = currentCellPos[0]
                        childCellElement[1] = currentCellPos[1]+1
                    if d == 'W':
                        childCellElement[0] = currentCellPos[0]
                        childCellElement[1] = currentCellPos[1]-1
                    if d == 'N':
                        childCellElement[0] = currentCellPos[0]-1 # TODO: 위로 갈때 -1인지 테스트 필요
                        childCellElement[1] = currentCellPos[1]
                    if d == 'S':
                        childCellElement[0] = currentCellPos[0]+1
                        childCellElement[1] = currentCellPos[1]
            
                    childCellPos = (childCellElement[0], childCellElement[1])
                    
                    temp_g_score = g_score[currentCellPos] + 1
                    temp_f_score = temp_g_score + self.Heuristic(childCellPos, goalPos)
                    
                    if temp_f_score < f_score[childCellPos]:
                        g_score[childCellPos] = temp_g_score
                        f_score[childCellPos] = temp_f_score
                        open.put((temp_f_score, self.Heuristic(childCellPos, goalPos), childCellPos))
                        aPath[childCellPos] = currentCellPos
        fwdPath = {}
        cell = goalPos
        while cell != startPos:
            fwdPath[aPath[cell]] = cell
            cell = aPath[cell]
        return fwdPath
    
    def BFS(self, cell_data, key: str):
        startPos = self.GetPlayerCellPos() # row, col 
        isVisited = [[False for col in len(cell_data[0])] for row in len(cell_data)] # !

        posVisited = deque()
        posVisited.append(startPos)
        
        dx = [0, 0, -1, 1] 
        dy = [-1, 1, 0, 0]
        isVisited[startPos[0]][startPos[1]] = True # !  
        
        while posVisited.count > 0:
            cur_x = posVisited[0][1] # !
            cur_y = posVisited[0][0] # ! 
            posVisited.popleft()
            for i in range(4):
                next_x = cur_x + dx[i]
                next_y = cur_y + dy[i]
                if next_x>=0 and next_x < len(cell_data[0]) and next_y>=0 and next_y < len(cell_data) and \
                    isVisited[next_y][next_x] is False and cell_data[next_y][next_x]['is_wall'] is False:
                        if cell_data[next_y][next_x][key]:
                            return (next_y, next_x)
                        
                        isVisited[next_y][next_x] = True
                        posVisited.append((next_y,next_x)) # ! 
                        
    def GetPlayerCellPos(self, cell_data):
        for rowCell in cell_data:
            for cell in rowCell:
                if cell['player'] == True:
                    return cell['grid'] # tuple
            
    # TODO: Implement here
    def GetNearestFoodCellPos(self, cell_data):
        return self.BFS(cell_data, "food")    

    # TODO: Implement here            
    def MovePlayerAI(self):
        fwdPath = {} # TODO: Get A star route 
        pass
    
m = maze(10,10) # maze top left 1,1 > bottom right 5,5 coordinate. x for row, y for col 
m.CreateMaze()

pathFinder = PathFinder()
path = pathFinder.AStarTest(m)

a = agent(m)
m.tracePath({a:path})

print(m.grid) # EWNS dictionary for each cell 
m.run()