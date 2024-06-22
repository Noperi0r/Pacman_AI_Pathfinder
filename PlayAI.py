import numpy as np
import heapq
import win32api, win32con
import cv2

class PacManAI:
    def __init__(self, cell_data = [], player_pos = (), ghosts_pos = [], edible_ghosts_pos = [], dots_pos = [], power_pellets_pos = []):
        self.cell_data = cell_data
        self.player_pos = player_pos
        self.ghosts_pos = ghosts_pos
        self.edible_ghosts_pos = edible_ghosts_pos
        self.dots_pos = dots_pos
        self.power_pellets_pos = power_pellets_pos
        self.power_mode = False
        self.power_mode_timer = 0
        
        self.player_next_pos = (0,0)
        self.path = []


    def print_path(self):
        print(f"Current path: {self.path}")



    # Should be called per frame
    def UpdateAIInfo(self, cell_data, player_pos, ghosts_pos, edible_ghosts_pos, dots_pos, power_pellets_pos):
        self.cell_data = cell_data
        self.player_pos = player_pos
        self.ghosts_pos = ghosts_pos
        self.edible_ghosts_pos = edible_ghosts_pos
        self.dots_pos = dots_pos
        self.power_pellets_pos = power_pellets_pos

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star_search(self, start, goal):
        neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)] # r, l, d, u 
        close_set = set()
        came_from = {}
        gscore = {start: 0}
        fscore = {start: self.heuristic(start, goal)}
        oheap = []

        heapq.heappush(oheap, (fscore[start], start))

        while oheap:
            current = heapq.heappop(oheap)[1]
            if current == goal:
                data = []
                for current in came_from:
                    try:
                        if not self.cell_data[current[0]][current[1]]["is_wall"]:
                            data.append(current)
                        current = came_from[current]
                        
                        # if self.cell_data[current[0]][current[1]]['is_wall']:
                        #     print(f"경로에 벽이 포함됨: {current}")
                        #     return False
                    except:
                        print("A-STAR: Exception handled")
                return data[::-1]

            close_set.add(current)
            for i, j in neighbors:
                neighbor = current[0] + i, current[1] + j
                tentative_g_score = 0
                if 0 <= neighbor[0] < len(self.cell_data) and 0 <= neighbor[1] < len(self.cell_data[0]) and not self.cell_data[neighbor[0]][neighbor[1]]['is_wall']:
                    #continue 
                    tentative_g_score = gscore[current] + self.heuristic(current, neighbor)
                    if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                        continue

                if neighbor not in [i[1] for i in oheap] or tentative_g_score < gscore.get(neighbor, 0):
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g_score
                    fscore[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(oheap, (fscore[neighbor], neighbor))
        return False

    def flee(self, player_pos, ghost_pos):
        neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        farthest = None
        max_dist = -1

        for i, j in neighbors:
            neighbor = player_pos[0] + i, player_pos[1] + j
            if 0 <= neighbor[0] < len(self.cell_data) and 0 <= neighbor[1] < len(self.cell_data[0]) and not self.cell_data[neighbor[0]][neighbor[1]]['is_wall']:
                dist = self.heuristic(neighbor, ghost_pos)
                if dist > max_dist:
                    max_dist = dist
                    farthest = neighbor
        return farthest

    def move_to(self, target):
        self.path = self.a_star_search(self.player_pos, target)
        if self.path:
            print(self.player_pos, " // ", self.path)
            return self.path[len(self.path)-1] # next position. MODIFIED: 1 to 0 
        else:
            print("move_to method ERROR: No path")
            return (-1, -1)
    
    def decide_next_pos(self):
        # if self.power_mode: # Priority 1: Power mode
        #     print("run: power mode")
        #     self.power_mode_timer -= 1
        #     if self.power_mode_timer <= 0:
        #         self.power_mode = False
        

        #     closest_ghost = min(self.ghosts_pos, key=lambda ghost: self.heuristic(self.player_pos, ghost))
        #     self.player_next_pos = self.move_to(closest_ghost)
        #     return self.player_next_pos
        
        # if self.ghosts_pos:
        #     for ghost_pos in self.ghosts_pos: # Prioriity 2: Flee
        #         if self.heuristic(self.player_pos, ghost_pos) < 5:  # If ghost is close
        #             print("run: ghosts pos")
        #             self.player_next_pos = self.flee(self.player_pos, ghost_pos)
        #             return self.player_next_pos
                

        
        # if self.power_pellets_pos:
        #     print("run: power pellets pos")
        #     closest_pellet = min(self.power_pellets_pos, key=lambda pellet: self.heuristic(self.player_pos, pellet))
        #     self.player_next_pos = self.move_to(closest_pellet)
        #     if self.player_next_pos == closest_pellet:
        #         self.power_mode = True
        #         self.power_mode_timer = 50  # Power mode duration
        #         self.power_pellets_pos.remove(closest_pellet)
        #     return self.player_next_pos
        
        if self.edible_ghosts_pos:
            closest_edible = min(self.edible_ghosts_pos, key=lambda edible: self.heuristic(self.player_pos, edible))
            self.player_next_pos = self.move_to(closest_edible)
            return self.player_next_pos
        
        if self.dots_pos:
            closest_dot = min(self.dots_pos, key=lambda dot: self.heuristic(self.player_pos, dot))
            self.player_next_pos = self.move_to(closest_dot)
            return self.player_next_pos
        
    def GiveInput(self, cell_data):
        # y, x
        try:
            cell_data[self.player_pos[0]][self.player_pos[1]]
        except:
            print(f"GiveInput: cell data index out of range by playerpos:{self.player_pos}")
            return None
        
        try:    
            cell_data[self.player_next_pos[0]][self.player_next_pos[1]]
        except:
            print(f"GiveInput: cell data index out of range by playerNextPos:{self.player_next_pos}")
            return None
            
        #print("GiveInput: " , self.player_pos, "->", self.player_next_pos)
        newPos = (self.player_next_pos[0] - self.player_pos[0], self.player_next_pos[1] - self.player_pos[1])
        
        inputTryNum = 100 # 1번만 input 주니까 잘 안돼서 여러번 매크로처럼 주려고 함 
        # 0 row y , 1 col x
        if newPos[0] == 0 and newPos[1] > 0: # Go right 
            for i in range(inputTryNum):
                win32api.keybd_event(win32con.VK_RIGHT, 0, 0, 0)
            print("RightArrow Pressed") 
            return "R"
            
        elif newPos[0] == 0 and newPos[1] < 0: # Go left 
            for i in range(inputTryNum):
                win32api.keybd_event(win32con.VK_LEFT, 0, 0, 0)
            print("LeftArrow Pressed") 
            return "L"
            
        elif newPos[0] < 0 and newPos[1] == 0: # Go up 
            for i in range(inputTryNum):
                win32api.keybd_event(win32con.VK_UP, 0, 0, 0)
            print("UpArrow Pressed") 
            return "U"
            
        elif newPos[0] > 0 and newPos[1] == 0: # Go down 
            for i in range(inputTryNum):
                win32api.keybd_event(win32con.VK_DOWN, 0, 0, 0)
            print("DownArrow Pressed") 
            return "D"
    
    def GetCurrentPlayerGrid(self, cell_data):
        for row in range(len(cell_data)):
            for col in range(len(cell_data[0])):
                if cell_data[row][col]['player'] == True:
                    return cell_data[row][col]['grid'] # return (row,col) of player cell 
    
    def PositionFeedback(self, dir:str, cell_data, app_frame, cell_width, cell_height):
        inputTryNum = 100
        
        curPos = self.GetCurrentPlayerGrid(cell_data)
        textPos = (cell_width * 22, cell_height * 14)        
        fontSize = 2
        if self.player_pos == curPos: # self.player_pos before update
            if dir == "R":
                for i in range(inputTryNum):
                    win32api.keybd_event(win32con.VK_LEFT, 0, 0, 0)
                print("Pos Feedback: To Left")
                cv2.putText(app_frame, "POS FEEDBACK: LEFT", textPos, cv2.FONT_HERSHEY_SIMPLEX, fontSize, (0, 255, 0), 5, cv2.LINE_AA)
                    
            elif dir == "L":
                for i in range(inputTryNum):
                    win32api.keybd_event(win32con.VK_RIGHT, 0, 0, 0)
                print("Pos Feedback: To Right")
                cv2.putText(app_frame, "POS FEEDBACK: RIGHT", textPos, cv2.FONT_HERSHEY_SIMPLEX, fontSize, (0, 255, 0), 5, cv2.LINE_AA)

            elif dir == "U":
                for i in range(inputTryNum):
                    win32api.keybd_event(win32con.VK_DOWN, 0, 0, 0)
                print("Pos Feedback: To Down")
                cv2.putText(app_frame, "POS FEEDBACK: DOWN", textPos, cv2.FONT_HERSHEY_SIMPLEX, fontSize, (0, 255, 0), 5, cv2.LINE_AA)

            elif dir == "D":
                for i in range(inputTryNum):
                    win32api.keybd_event(win32con.VK_UP, 0, 0, 0)
                print("Pos Feedback: To Up")
                cv2.putText(app_frame, "POS FEEDBACK: UP", textPos, cv2.FONT_HERSHEY_SIMPLEX, fontSize, (0, 255, 0), 5, cv2.LINE_AA)

        

        
        