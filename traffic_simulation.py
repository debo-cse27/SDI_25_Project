import pygame
import time
import random
from traffic_light_controller import TrafficJunction, get_traffic_density, get_signal_timing
import multiprocessing

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
LANE_WIDTH = 120
VEHICLE_WIDTH, VEHICLE_HEIGHT = 40, 20
TRAFFIC_LIGHT_SIZE = 30
FPS = 60
JUNCTION_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Colors
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

class Vehicle:
    def __init__(self, lane, direction):
        self.lane = lane
        self.direction = direction
        self.speed = random.randint(2, 4)
        
        # Set initial position based on lane
        if direction == 'horizontal':
            self.y = JUNCTION_CENTER[1] - LANE_WIDTH//2 if lane == 0 else JUNCTION_CENTER[1] + LANE_WIDTH//2
            self.x = 0 if lane == 0 else SCREEN_WIDTH
            self.speed = self.speed if lane == 0 else -self.speed
        else:  # vertical
            self.x = JUNCTION_CENTER[0] - LANE_WIDTH//2 if lane == 0 else JUNCTION_CENTER[0] + LANE_WIDTH//2
            self.y = 0 if lane == 0 else SCREEN_HEIGHT
            self.speed = self.speed if lane == 0 else -self.speed

    def move(self, light_status):
        if light_status == 'GREEN':
            if self.direction == 'horizontal':
                self.x += self.speed
            else:
                self.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, (self.x, self.y, VEHICLE_WIDTH, VEHICLE_HEIGHT))

    def is_out_of_bounds(self):
        return (self.x < -VEHICLE_WIDTH or self.x > SCREEN_WIDTH or 
                self.y < -VEHICLE_HEIGHT or self.y > SCREEN_HEIGHT)

class TrafficSimulation:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Traffic Light Simulation")
        
        # Initialize traffic junction with the same configuration as your main system
        self.lanes = [
            {
                'current': 'static/images/lane1_current.jpg',
                'reference': 'static/images/lane1_empty.jpg'
            },
            {
                'current': 'static/images/lane2_current.jpg',
                'reference': 'static/images/lane2_empty.jpg'
            },
            {
                'current': 'static/images/lane3_current.jpg',
                'reference': 'static/images/lane3_empty.jpg'
            },
            {
                'current': 'static/images/lane4_current.jpg',
                'reference': 'static/images/lane4_empty.jpg'
            }
        ]
        
        self.junction = TrafficJunction(self.lanes)
        self.vehicles = []
        self.current_state = {
            'active_lane': 0,
            'timer': 0,
            'light_status': 'RED',
            'density': 0
        }
        
        self.clock = pygame.time.Clock()

    def add_vehicle(self):
        if random.random() < 0.02:  # 2% chance each frame to add a new vehicle
            lane = random.randint(0, 3)
            direction = 'horizontal' if lane < 2 else 'vertical'
            self.vehicles.append(Vehicle(lane % 2, direction))

    def draw_roads(self):
        # Draw horizontal roads
        pygame.draw.rect(self.screen, GRAY, 
                        (0, JUNCTION_CENTER[1] - LANE_WIDTH, SCREEN_WIDTH, LANE_WIDTH * 2))
        # Draw vertical roads
        pygame.draw.rect(self.screen, GRAY, 
                        (JUNCTION_CENTER[0] - LANE_WIDTH, 0, LANE_WIDTH * 2, SCREEN_HEIGHT))

    def draw_traffic_lights(self):
        light_positions = [
            (JUNCTION_CENTER[0] - LANE_WIDTH, JUNCTION_CENTER[1] - LANE_WIDTH),  # Left
            (JUNCTION_CENTER[0] + LANE_WIDTH, JUNCTION_CENTER[1] + LANE_WIDTH),  # Right
            (JUNCTION_CENTER[0] - LANE_WIDTH, JUNCTION_CENTER[1] - LANE_WIDTH),  # Top
            (JUNCTION_CENTER[0] + LANE_WIDTH, JUNCTION_CENTER[1] + LANE_WIDTH)   # Bottom
        ]
        
        for i, pos in enumerate(light_positions):
            color = GREEN if (i == self.current_state['active_lane'] - 1 and 
                            self.current_state['light_status'] == 'GREEN') else \
                    YELLOW if (i == self.current_state['active_lane'] - 1 and 
                             self.current_state['light_status'] == 'YELLOW') else RED
            pygame.draw.circle(self.screen, color, pos, TRAFFIC_LIGHT_SIZE)

    def run(self):
        running = True
        last_time = time.time()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Process traffic logic
            current_time = time.time()
            if current_time - last_time >= 1:  # Update every second
                if self.current_state['timer'] <= 0:
                    self.current_state['active_lane'] = (self.current_state['active_lane'] % 4) + 1
                    timing, density = self.junction.process_lane(self.current_state['active_lane'] - 1)
                    self.current_state['density'] = density
                    self.current_state['timer'] = timing
                    self.current_state['light_status'] = 'GREEN'
                else:
                    self.current_state['timer'] -= 1
                    if self.current_state['timer'] <= 3 and self.current_state['light_status'] == 'GREEN':
                        self.current_state['light_status'] = 'YELLOW'
                last_time = current_time

            # Update simulation
            self.screen.fill(WHITE)
            self.draw_roads()
            self.draw_traffic_lights()
            self.add_vehicle()

            # Update and draw vehicles
            for vehicle in self.vehicles[:]:
                vehicle.move(self.current_state['light_status'])
                vehicle.draw(self.screen)
                if vehicle.is_out_of_bounds():
                    self.vehicles.remove(vehicle)

            # Display current state
            font = pygame.font.Font(None, 36)
            status_text = f"Lane: {self.current_state['active_lane']} | Timer: {self.current_state['timer']} | Status: {self.current_state['light_status']}"
            text_surface = font.render(status_text, True, BLACK)
            self.screen.blit(text_surface, (10, 10))

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

def launch_simulation_process():
    """Function to launch simulation in a separate process"""
    simulation = TrafficSimulation()
    simulation.run()

def start_simulation():
    """Start the simulation in a separate process"""
    process = multiprocessing.Process(target=launch_simulation_process)
    process.start()
    return process

if __name__ == "__main__":
    launch_simulation_process() 