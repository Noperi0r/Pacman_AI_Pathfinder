import cv2
import numpy as np
import heapq

class PacManAI:
    def __init__(self, grid, player_pos, ghosts_pos, dots_pos, power_pellets_pos):
        self.grid = grid
        self.player_pos = player_pos
        self.ghosts_pos = ghosts_pos
        self.dots_pos = dots_pos
        self.power_pellets_pos = power_pellets_pos
        self.power_mode = False
        self.power_mode_timer = 0

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star_search(self, start, goal):
        neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
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
                while current in came_from:
                    data.append(current)
                    current = came_from[current]
                return data[::-1]

            close_set.add(current)
            for i, j in neighbors:
                neighbor = current[0] + i, current[1] + j
                if 0 <= neighbor[0] < self.grid.shape[0] and 0 <= neighbor[1] < self.grid.shape[1] and self.grid[neighbor[0]][neighbor[1]] == 1:
                    continue

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
            if 0 <= neighbor[0] < self.grid.shape[0] and 0 <= neighbor[1] < self.grid.shape[1] and self.grid[neighbor[0]][neighbor[1]] == 0:
                dist = self.heuristic(neighbor, ghost_pos)
                if dist > max_dist:
                    max_dist = dist
                    farthest = neighbor

        return farthest

    def move_to(self, target):
        path = self.a_star_search(self.player_pos, target)
        if path:
            self.player_pos = path[1]  # Move to the next point in the path
        return self.player_pos

    def run(self):
        if self.power_mode:
            self.power_mode_timer -= 1
            if self.power_mode_timer <= 0:
                self.power_mode = False

            closest_ghost = min(self.ghosts_pos, key=lambda ghost: self.heuristic(self.player_pos, ghost))
            self.player_pos = self.move_to(closest_ghost)
            return self.player_pos

        if self.power_pellets_pos:
            closest_pellet = min(self.power_pellets_pos, key=lambda pellet: self.heuristic(self.player_pos, pellet))
            self.player_pos = self.move_to(closest_pellet)
            if self.player_pos == closest_pellet:
                self.power_mode = True
                self.power_mode_timer = 50  # Power mode duration
                self.power_pellets_pos.remove(closest_pellet)
            return self.player_pos

        for ghost_pos in self.ghosts_pos:
            if self.heuristic(self.player_pos, ghost_pos) < 5:  # If ghost is close
                self.player_pos = self.flee(self.player_pos, ghost_pos)
                return self.player_pos

        closest_dot = min(self.dots_pos, key=lambda dot: self.heuristic(self.player_pos, dot))
        self.player_pos = self.move_to(closest_dot)
        return self.player_pos

# Load YOLO
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# Load screenshot
screenshot = cv2.imread('screenshot.png')

# Convert BGR to RGB
rgb_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)

# Detect objects in the screenshot
blob = cv2.dnn.blobFromImage(screenshot, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
net.setInput(blob)
outs = net.forward(output_layers)

# Initialize lists to hold detected object positions
player_pos = None
ghosts_pos = []
dots_pos = []
pellets_pos = []

# Loop over detections
for out in outs:
    for detection in out:
        scores = detection[5:]
        class_id = np.argmax(scores)
        confidence = scores[class_id]
        if confidence > 0.5:  # Adjust confidence threshold as needed
            center_x = int(detection[0] * screenshot.shape[1])
            center_y = int(detection[1] * screenshot.shape[0])
            w = int(detection[2] * screenshot.shape[1])
            h = int(detection[3] * screenshot.shape[0])
            x = int(center_x - w / 2)
            y = int(center_y - h / 2)

            if class_id == 0:  # Assuming 0 is the class id for player
                player_pos = (center_x, center_y)
            elif class_id == 1:  # Assuming 1 is the class id for ghosts
                ghosts_pos.append((center_x, center_y))
            elif class_id == 2:  # Assuming 2 is the class id for dots
                dots_pos.append((center_x, center_y))
            elif class_id == 3:  # Assuming 3 is the class id for pellets
                pellets_pos.append((center_x, center_y))

# Create grid based on screenshot dimensions
grid = np.zeros((screenshot.shape[0], screenshot.shape[1]))

# Initialize PacManAI
ai = PacManAI(grid, player_pos, ghosts_pos, dots_pos, pellets_pos)

# Main loop
while True:
    next_move = ai.run()
    # Update player position in the game
    # Example: update_player_position(next_move)

    # Check if player is caught by a ghost
    if ai.player_pos in ai.ghosts_pos:
        print("Game Over! You've been caught by a ghost.")
        break

    # Check if all dots are eaten
    if len(ai.dots_pos) == 0:
        print("Congratulations! You've eaten all the dots and won!")
        break
