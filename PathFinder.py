from pyamaze import maze, agent
from queue import PriorityQueue

class PathFinder:
    def __init__(self):
        pass
    
    # Heuristic based on manhattan distance 
    def Heuristic(self, cell1, cell2): 
        x1, y1 = cell1
        x2, y2 = cell2
        
        return abs(x1 - x2) + abs(y1 - y2) 
    
    def AStarTest(self, m: maze):
        start = (m.rows, m.cols)
        goal = (1,1) # TODO: Change 1,1
        
        gScore = {cell:float('inf') for cell in m.grid } # gScore: Distance passed 
        gScore[start] = 0
        
        fScore = {cell:float('inf') for cell in m.grid } # fScore: Heuristic + gScor
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
    
m = maze(10,10) # maze top left 1,1 > bottom right 5,5 coordinate. x for row, y for col 
m.CreateMaze()

pathFinder = PathFinder()
path = pathFinder.AStarTest(m)

a = agent(m)
m.tracePath({a:path})

print(m.maze_map) # EWNS dictionary for each cell 
m.run()