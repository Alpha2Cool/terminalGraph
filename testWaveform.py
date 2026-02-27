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

def drawWaveform(data, windowSize, currentIndex):
    if not data:
        return
    
    # Find min and max values for normalization
    minVal = min(data)
    maxVal = max(data)
    rangeVal = maxVal - minVal
    if rangeVal == 0:
        rangeVal = 1  # Avoid division by zero
    
    # Terminal dimensions (adjustable)
    width = 80
    height = 20
    
    # Create grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Draw waveform
    for i in range(len(data)):
        normalized = (data[i] - minVal) / rangeVal
        y = height - 1 - int(normalized * (height - 2))
        # Ensure y is within bounds
        y = max(0, min(y, height - 1))
        if len(data) > 1:
            x = int((i * (width - 10)) / (len(data) - 1))
        else:
            x = 10  # Default position for single data point
        # Ensure x is within bounds
        x = max(0, min(x, width - 1))
        grid[y][x] = '*'
    
    # Draw axes
    for y in range(height):
        grid[y][9] = '|'
    for x in range(9, width):
        grid[height - 1][x] = '-'
    grid[height - 1][9] = '+'
    
    # Clear screen
    print('\n' * 50)
    
    # Draw header
    print("=======================================")
    print("Real-time Waveform Display")
    print(f"Window Size: {windowSize} | Current Index: {currentIndex}")
    print(f"Data Points: {len(data)}")
    print(f"Range: {minVal:.2f} to {maxVal:.2f}")
    print("=======================================")
    
    # Draw scale on y-axis
    print(f"{maxVal:9.2f} |")
    for y in range(1, height - 1):
        val = maxVal - (y * rangeVal) / (height - 2)
        print(f"{val:9.2f} |", end="")
        for x in range(10, width):
            print(grid[y][x], end="")
        print()
    print(f"{minVal:9.2f} |", end="")
    for x in range(10, width):
        print(grid[height - 1][x], end="")
    print()
    
    # Draw x-axis labels
    print(" " * 10, end="")
    if len(data) > 1:
        for i in range(5):
            x = 10 + (i * (width - 10)) // 4
            label = i * (len(data) - 1) // 4
            print(f"{label:^{ (width - 10) // 4 }}", end="")
    elif len(data) == 1:
        print(f"{'0':^{ (width - 10) // 2 }}", end="")
    print()
    
    # Draw unit
    print("Unit: normalized")
    print("=======================================")
    print("Press Ctrl+C to exit")
    print("=======================================")

def main():
    try:
        config = parseArgs(sys.argv)
        if not config.is2D or not config.dataFile:
            print("Usage: testWaveform.py -2d -f dataFile [-w windowSize]")
            return 1
        
        # Open the data file
        with open(config.dataFile, 'r') as file:
            # Maintain a sliding window of data
            windowData = []
            totalDataCount = 0
            
            # Read data line by line (simulating real-time data arrival)
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
                        
                        # Draw the current window
                        drawWaveform(windowData, config.windowSize, totalDataCount)
                        
                        # Add a small delay to simulate real-time data acquisition
                        time.sleep(0.05)
                        
                    except ValueError:
                        print(f"Warning: Invalid data in line: {line}")
                        continue
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()