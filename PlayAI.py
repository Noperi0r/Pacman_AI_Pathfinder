import cv2
import numpy as np
import torch
import heapq
from yolov5.models.common import DetectMultiBackend
from yolov5.utils.datasets import LoadImages
from yolov5.utils.general import non_max_suppression, scale_coords

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

# Load YOLOv5 model
model = DetectMultiBackend(weights='best.pt', device='cpu')  # Adjust device as needed
stride, names, pt = model.stride, model.names, model.pt

def detect_objects(image):
    img = [LoadImages(image, img_size=640, stride=stride, auto=pt)]
    for path, img, im0s, vid_cap in img:
        img = torch.from_numpy(img).to(model.device)
        img = img.float() / 255.0  # Normalize
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        pred = model(img, augment=False, visualize=False)
        pred = non_max_suppression(pred, 0.25, 0.45, classes=None, agnostic=False)
        det = pred[0]

        gn = torch.tensor(im0s.shape)[[1, 0, 1, 0]]  # normalization gain whwh
        if len(det):
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0s.shape).round()
        
        detected_objects = []
        for *xyxy, conf, cls in det:
            x1, y1, x2, y2 = map(int, xyxy)
            detected_objects.append((names[int(cls)], (x1, y1, x2 - x1, y2 - y2)))
        return detected_objects

# Load screenshot
screenshot = 'screenshot.png'

# Detect objects using YOLO
detected_objects = detect_objects(screenshot)

# Map detected objects to their positions
player_pos = None
ghosts_pos = []
dots_pos = []
pellets_pos = []

for obj_name, box in detected_objects:
    x, y, w, h = box
    center = (x + w // 2, y + h // 2)
    if obj_name == "player":
        player_pos = center
    elif obj_name == "ghost":
        ghosts_pos.append(center)
    elif obj_name == "dot":
        dots_pos.append(center)
    elif obj_name == "pellet":
        pellets_pos.append(center)

if player_pos is None:
    player_pos = (10, 10)  # Default starting position if player is not detected

# Initialize PacManAI
ai = PacManAI(np.zeros((screenshot.shape[:2])), player_pos, ghosts_pos, dots_pos, pellets_pos)

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
