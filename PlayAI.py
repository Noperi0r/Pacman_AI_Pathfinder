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

    # def a_star_search(self, start, goal):
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

                if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                    continue

                tentative_g_score = gscore[current] + self.heuristic(current, neighbor)
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

# Load screenshot
screenshot = cv2.imread('screenshot.png')

# Convert BGR to RGB
rgb_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)

# Define color thresholds for two types of ghosts
ghost1_lower = np.array([0, 0, 128], dtype=np.uint8)
ghost1_upper = np.array([128, 128, 255], dtype=np.uint8)
ghost2_lower = np.array([128, 0, 0], dtype=np.uint8)
ghost2_upper = np.array([255, 128, 128], dtype=np.uint8)
dot_lower = np.array([0, 128, 0], dtype=np.uint8)
dot_upper = np.array([128, 255, 128], dtype=np.uint8)
pellet_lower = np.array([200, 200, 200], dtype=np.uint8)
pellet_upper = np.array([255, 255, 255], dtype=np.uint8)

# Thresholding for two types of ghosts
ghost1_mask = cv2.inRange(rgb_screenshot, ghost1_lower, ghost1_upper)
ghost2_mask = cv2.inRange(rgb_screenshot, ghost2_lower, ghost2_upper)
dot_mask = cv2.inRange(rgb_screenshot, dot_lower, dot_upper)
pellet_mask = cv2.inRange(rgb_screenshot, pellet_lower, pellet_upper)

# Find contours for two types of ghosts
ghost1_contours, _ = cv2.findContours(ghost1_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
ghost2_contours, _ = cv2.findContours(ghost2_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
dot_contours, _ = cv2.findContours(dot_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
pellet_contours, _ = cv2.findContours(pellet_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Extract positions for two types of ghosts
ghosts1_pos = [tuple(c[0]) for c in ghost1_contours]
ghosts2_pos = [tuple(c[0]) for c in ghost2_contours]
dots_pos = [tuple(c[0]) for c in dot_contours]
pellets_pos = [tuple(c[0]) for c in pellet_contours]

# Initial player position
player_pos = (10, 10)  # Example starting position

# Initialize PacManAI
ai = PacManAI(np.zeros(rgb_screenshot.shape[:2]), player_pos, ghosts1_pos + ghosts2_pos, dots_pos, pellets_pos)

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

