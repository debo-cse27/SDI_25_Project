import cv2
import numpy as np
import time

def get_traffic_density(current_image_path, reference_image_path):
    """
    Compare current traffic image with reference empty road image
    Returns matching percentage
    """
    # Read both images
    current_img = cv2.imread(current_image_path)
    reference_img = cv2.imread(reference_image_path)
    
    # Convert images to grayscale
    current_gray = cv2.cvtColor(current_img, cv2.COLOR_BGR2GRAY)
    reference_gray = cv2.cvtColor(reference_img, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    current_blur = cv2.GaussianBlur(current_gray, (5, 5), 0)
    reference_blur = cv2.GaussianBlur(reference_gray, (5, 5), 0)
    
    # Apply Canny edge detection
    current_edges = cv2.Canny(current_blur, 50, 150)
    reference_edges = cv2.Canny(reference_blur, 50, 150)
    
    # Calculate matching percentage using structural similarity
    # Higher score means more similarity (less traffic)
    score = cv2.matchTemplate(current_edges, reference_edges, cv2.TM_CCOEFF_NORMED)
    matching_percentage = (score[0][0] + 1) * 50  # Normalize to 0-100 range
    
    return matching_percentage

def get_signal_timing(matching_percentage):
    """
    Determine green light duration based on matching percentage
    """
    if matching_percentage >= 90:
        return 10
    elif 70 <= matching_percentage < 90:
        return 20
    elif 50 <= matching_percentage < 70:
        return 30
    elif 10 <= matching_percentage < 50:
        return 60
    else:
        return 90

class TrafficJunction:
    def __init__(self, lanes):
        """
        Initialize traffic junction with lane configurations
        lanes: list of dictionaries containing current and reference image paths for each lane
        """
        self.lanes = lanes
        self.current_lane = 0
    
    def process_lane(self, lane_number):
        """
        Process a single lane and return required green light duration
        """
        lane = self.lanes[lane_number]
        density = get_traffic_density(lane['current'], lane['reference'])
        timing = get_signal_timing(density)
        return timing, density
    
    def run_traffic_cycle(self):
        """
        Run a complete traffic signal cycle for all lanes
        """
        for i in range(len(self.lanes)):
            print(f"\nProcessing Lane {i+1}")
            timing, density = self.process_lane(i)
            
            print(f"Traffic Density Match: {density:.2f}%")
            print(f"Green Light Duration: {timing} seconds")
            
            # Simulate traffic light timing
            print("GREEN light ON")
            time.sleep(timing)
            print("GREEN light OFF")
            
            # Yellow light transition
            print("YELLOW light ON")
            time.sleep(3)
            print("YELLOW light OFF")

def main():
    # Example configuration for a 4-way junction
    lanes = [
        {
            'current': 'lane1_current.jpg',
            'reference': 'lane1_empty.jpg'
        },
        {
            'current': 'lane2_current.jpg',
            'reference': 'lane2_empty.jpg'
        },
        {
            'current': 'lane3_current.jpg',
            'reference': 'lane3_empty.jpg'
        },
        {
            'current': 'lane4_current.jpg',
            'reference': 'lane4_empty.jpg'
        }
    ]
    
    # Initialize and run traffic junction
    junction = TrafficJunction(lanes)
    
    try:
        while True:
            print("\nStarting new traffic cycle...")
            junction.run_traffic_cycle()
    except KeyboardInterrupt:
        print("\nTraffic system stopped.")

if __name__ == "__main__":
    main() 