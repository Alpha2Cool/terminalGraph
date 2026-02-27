import sys
import time

class Config:
    def __init__(self):
        self.is2D = False
        self.dataFile = ""
        self.windowSize = 100

def parseArgs(argv):
    config = Config()
    i = 1
    while i < len(argv):
        arg = argv[i]
        if arg == "-2d":
            config.is2D = True
        elif arg == "-f" and i + 1 < len(argv):
            config.dataFile = argv[i + 1]
            i += 1
        elif arg == "-w" and i + 1 < len(argv):
            config.windowSize = int(argv[i + 1])
            i += 1
        i += 1
    return config

def calculateRange(data):
    """Calculate the min and max values for the entire dataset"""
    minVal = min(data)
    maxVal = max(data)
    rangeVal = maxVal - minVal
    if rangeVal == 0:
        rangeVal = 1  # Avoid division by zero
    return minVal, maxVal, rangeVal

def clearScreen():
    """Clear the terminal screen"""
    # Use a more compatible way to clear the screen
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def drawInitialScreen(width, height, minVal, maxVal, rangeVal, windowSize):
    """Draw the initial screen with axes"""
    # Clear screen
    clearScreen()
    
    # Draw header
    print("=======================================")
    print("Real-time Waveform Display")
    print(f"Window Size: {windowSize}")
    print(f"Range: {minVal:.2f} to {maxVal:.2f}")
    print("=======================================")
    
    # Draw scale on y-axis
    print(f"{maxVal:9.2f} |")
    for y in range(1, height - 1):
        val = maxVal - (y * rangeVal) / (height - 2)
        print(f"{val:9.2f} |" + " " * (width - 10))
    print(f"{minVal:9.2f} |" + "-" * (width - 10))
    
    # Draw x-axis labels
    print(" " * 10, end="")
    for i in range(5):
        label = i * (windowSize - 1) // 4
        print(f"{label:^{ (width - 10) // 4 }}", end="")
    print()
    
    # Draw unit
    print("Unit: normalized")
    print("=======================================")
    print("Press Ctrl+C to exit")
    print("=======================================")
    print("Current Index: 0")

def updateWaveform(data, width, height, minVal, maxVal, rangeVal, currentIndex):
    """Update only the waveform points"""
    # Clear the screen and redraw everything (more reliable approach)
    clearScreen()
    
    # Redraw header
    print("=======================================")
    print("Real-time Waveform Display")
    print(f"Window Size: {len(data)}")
    print(f"Range: {minVal:.2f} to {maxVal:.2f}")
    print("=======================================")
    
    # Calculate waveform points positions
    waveform_points = []
    for i in range(len(data)):
        normalized = (data[i] - minVal) / rangeVal
        y = height - 1 - int(normalized * (height - 2))
        # Ensure y is within bounds
        y = max(0, min(y, height - 1))
        if len(data) > 1:
            x = int((i * (width - 10)) / (len(data) - 1))
        else:
            x = 0
        # Ensure x is within bounds
        x = max(0, min(x, width - 11))
        waveform_points.append((y, x))
    
    # Create a 2D grid for the waveform
    grid = [[" " for _ in range(width - 10)] for _ in range(height)]
    
    # Draw waveform points
    for y, x in waveform_points:
        if 0 <= y < height and 0 <= x < width - 10:
            grid[y][x] = "*"
    
    # Draw simple lines between consecutive points to make the waveform more continuous
    for i in range(1, len(waveform_points)):
        prev_y, prev_x = waveform_points[i-1]
        curr_y, curr_x = waveform_points[i]
        
        # Only draw lines if the points are close enough to avoid cluttering
        if abs(curr_y - prev_y) <= 2 and abs(curr_x - prev_x) <= 2:
            # Draw horizontal line
            if curr_y == prev_y:
                start_x = min(prev_x, curr_x)
                end_x = max(prev_x, curr_x)
                for x_line in range(start_x, end_x + 1):
                    if 0 <= x_line < width - 10:
                        grid[curr_y][x_line] = "*"
            # Draw vertical line
            elif curr_x == prev_x:
                start_y = min(prev_y, curr_y)
                end_y = max(prev_y, curr_y)
                for y_line in range(start_y, end_y + 1):
                    if 0 <= y_line < height:
                        grid[y_line][curr_x] = "*"
    
    # Redraw Y-axis with waveform
    for y in range(height):
        # Calculate the Y-axis value
        if y == 0:
            val = maxVal
        elif y == height - 1:
            val = minVal
        else:
            val = maxVal - (y * rangeVal) / (height - 2)
        
        # Print Y-axis label
        print(f"{val:9.2f} |", end="")
        
        # Print the waveform for this line
        print("" .join(grid[y]), end="")
        print()
    
    # Redraw X-axis labels
    print(" " * 10, end="")
    for i in range(5):
        label = i * (len(data) - 1) // 4
        print(f"{label:^{ (width - 10) // 4 }}", end="")
    print()
    
    # Redraw unit
    print("Unit: normalized")
    print("=======================================")
    print("Press Ctrl+C to exit")
    print("=======================================")
    print(f"Current Index: {currentIndex}")

def main():
    try:
        config = parseArgs(sys.argv)
        if not config.is2D or not config.dataFile:
            print("Usage: terminalGraph.py -2d -f dataFile [-w windowSize]")
            return 1
        
        # First pass: read all data to calculate range
        allData = []
        try:
            with open(config.dataFile, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line:
                        try:
                            value = float(line)
                            allData.append(value)
                        except ValueError:
                            continue
        except Exception as e:
            print(f"Error reading file: {e}")
            return 1
        
        if not allData:
            print("Error: No valid data found in file")
            return 1
        
        # Calculate range for fixed scale
        minVal, maxVal, rangeVal = calculateRange(allData)
        
        # Terminal dimensions
        width = 80
        height = 20
        
        # Display data in real-time with sliding window
        windowData = []
        totalDataCount = 0
        
        try:
            with open(config.dataFile, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line:
                        try:
                            value = float(line)
                            # Add new data to the window
                            windowData.append(value)
                            totalDataCount += 1
                            
                            # If window exceeds size, remove the oldest data
                            if len(windowData) > config.windowSize:
                                windowData.pop(0)
                            
                            # Update the waveform
                            updateWaveform(windowData, width, height, minVal, maxVal, rangeVal, totalDataCount)
                            
                            # Add a small delay to simulate real-time data acquisition
                            time.sleep(0.03)
                            
                        except ValueError:
                            continue
        except Exception as e:
            print(f"Error reading file: {e}")
            return 1
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()