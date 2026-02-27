#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <algorithm>
#include <windows.h>
#include <sstream>

class Config {
public:
    bool is2D;
    std::string dataFile;
    int windowSize;

    Config() : is2D(false), windowSize(100) {}
};

Config parseArgs(int argc, char* argv[]) {
    Config config;
    int i = 1;
    while (i < argc) {
        std::string arg = argv[i];
        if (arg == "-2d") {
            config.is2D = true;
        } else if (arg == "-f" && i + 1 < argc) {
            config.dataFile = argv[i + 1];
            i++;
        } else if (arg == "-w" && i + 1 < argc) {
            config.windowSize = std::stoi(argv[i + 1]);
            i++;
        }
        i++;
    }
    return config;
}

void calculateRange(const std::vector<double>& data, double& minVal, double& maxVal, double& rangeVal) {
    minVal = *std::min_element(data.begin(), data.end());
    maxVal = *std::max_element(data.begin(), data.end());
    rangeVal = maxVal - minVal;
    if (rangeVal == 0) {
        rangeVal = 1; // Avoid division by zero
    }
}

void clearScreen() {
    system("cls");
}

void updateWaveform(const std::vector<double>& data, int width, int height, double minVal, double maxVal, double rangeVal, int currentIndex) {
    // Clear the screen
    clearScreen();

    // Draw header
    std::cout << "=======================================\n";
    std::cout << "Real-time Waveform Display\n";
    std::cout << "Window Size: " << data.size() << "\n";
    std::cout << "Range: " << minVal << " to " << maxVal << "\n";
    std::cout << "=======================================\n";

    // Calculate waveform points positions
    std::vector<std::pair<int, int>> waveformPoints;
    for (size_t i = 0; i < data.size(); i++) {
        double normalized = (data[i] - minVal) / rangeVal;
        int y = height - 1 - static_cast<int>(normalized * (height - 2));
        // Ensure y is within bounds
        y = std::max<int>(0, std::min<int>(y, height - 1));
        int x;
        if (data.size() > 1) {
            x = static_cast<int>((i * (width - 10)) / (data.size() - 1));
        } else {
            x = 0;
        }
        // Ensure x is within bounds
        x = std::max<int>(0, std::min<int>(x, width - 11));
        waveformPoints.emplace_back(y, x);
    }

    // Create a 2D grid for the waveform
    std::vector<std::vector<char>> grid(height, std::vector<char>(width - 10, ' '));

    // Draw waveform points
    for (const auto& point : waveformPoints) {
        int y = point.first;
        int x = point.second;
        if (y >= 0 && y < height && x >= 0 && x < width - 10) {
            grid[y][x] = '*';
        }
    }

    // Draw simple lines between consecutive points to make the waveform more continuous
    for (size_t i = 1; i < waveformPoints.size(); i++) {
        int prevY = waveformPoints[i - 1].first;
        int prevX = waveformPoints[i - 1].second;
        int currY = waveformPoints[i].first;
        int currX = waveformPoints[i].second;

        // Only draw lines if the points are close enough to avoid cluttering
        if (std::abs(currY - prevY) <= 2 && std::abs(currX - prevX) <= 2) {
            // Draw horizontal line
            if (currY == prevY) {
                int startX = std::min<int>(prevX, currX);
                int endX = std::max<int>(prevX, currX);
                for (int x = startX; x <= endX; x++) {
                    if (x >= 0 && x < width - 10) {
                        grid[currY][x] = '*';
                    }
                }
            }
            // Draw vertical line
            else if (currX == prevX) {
                int startY = std::min<int>(prevY, currY);
                int endY = std::max<int>(prevY, currY);
                for (int y = startY; y <= endY; y++) {
                    if (y >= 0 && y < height) {
                        grid[y][currX] = '*';
                    }
                }
            }
        }
    }

    // Draw Y-axis with waveform
    for (int y = 0; y < height; y++) {
        // Calculate the Y-axis value
        double val;
        if (y == 0) {
            val = maxVal;
        } else if (y == height - 1) {
            val = minVal;
        } else {
            val = maxVal - (y * rangeVal) / (height - 2);
        }

        // Print Y-axis label
        std::cout << std::fixed;
        std::cout.precision(2);
        std::cout.width(9);
        std::cout << val << " |";

        // Print the waveform for this line
        for (int x = 0; x < width - 10; x++) {
            std::cout << grid[y][x];
        }
        std::cout << "\n";
    }

    // Draw X-axis labels
    std::cout << std::string(10, ' ');
    for (int i = 0; i < 5; i++) {
        int label = i * (data.size() - 1) / 4;
        std::stringstream ss;
        ss << label;
        std::string labelStr = ss.str();
        int padding = (width - 10) / 4;
        int leftPad = (padding - labelStr.length()) / 2;
        int rightPad = padding - leftPad - labelStr.length();
        std::cout << std::string(leftPad, ' ') << labelStr << std::string(rightPad, ' ');
    }
    std::cout << "\n";

    // Draw unit
    std::cout << "Unit: normalized\n";
    std::cout << "=======================================\n";
    std::cout << "Press Ctrl+C to exit\n";
    std::cout << "=======================================\n";
    std::cout << "Current Index: " << currentIndex << "\n";
}

int main(int argc, char* argv[]) {
    try {
        Config config = parseArgs(argc, argv);
        if (!config.is2D || config.dataFile.empty()) {
            std::cout << "Usage: terminalGraph -2d -f dataFile [-w windowSize]\n";
            return 1;
        }

        // First pass: read all data to calculate range
        std::vector<double> allData;
        try {
            std::ifstream file(config.dataFile);
            if (!file.is_open()) {
                std::cout << "Error: Could not open file\n";
                return 1;
            }

            std::string line;
            while (std::getline(file, line)) {
                // Trim whitespace
                size_t start = line.find_first_not_of(" \t");
                size_t end = line.find_last_not_of(" \t");
                if (start != std::string::npos && end != std::string::npos) {
                    line = line.substr(start, end - start + 1);
                } else {
                    continue; // Skip empty lines
                }

                try {
                    double value = std::stod(line);
                    allData.push_back(value);
                } catch (const std::invalid_argument&) {
                    continue; // Skip non-numeric lines
                }
            }
            file.close();
        } catch (const std::exception& e) {
            std::cout << "Error reading file: " << e.what() << "\n";
            return 1;
        }

        if (allData.empty()) {
            std::cout << "Error: No valid data found in file\n";
            return 1;
        }

        // Calculate range for fixed scale
        double minVal, maxVal, rangeVal;
        calculateRange(allData, minVal, maxVal, rangeVal);

        // Terminal dimensions
        int width = 80;
        int height = 20;

        // Display data in real-time with sliding window
        std::vector<double> windowData;
        int totalDataCount = 0;

        try {
            std::ifstream file(config.dataFile);
            if (!file.is_open()) {
                std::cout << "Error: Could not open file\n";
                return 1;
            }

            std::string line;
            while (std::getline(file, line)) {
                // Trim whitespace
                size_t start = line.find_first_not_of(" \t");
                size_t end = line.find_last_not_of(" \t");
                if (start != std::string::npos && end != std::string::npos) {
                    line = line.substr(start, end - start + 1);
                } else {
                    continue; // Skip empty lines
                }

                try {
                    double value = std::stod(line);
                    // Add new data to the window
                    windowData.push_back(value);
                    totalDataCount++;

                    // If window exceeds size, remove the oldest data
                    if (windowData.size() > config.windowSize) {
                        windowData.erase(windowData.begin());
                    }

                    // Update the waveform
                    updateWaveform(windowData, width, height, minVal, maxVal, rangeVal, totalDataCount);

                    // Add a small delay to simulate real-time data acquisition
                    Sleep(30);

                } catch (const std::invalid_argument&) {
                    continue; // Skip non-numeric lines
                }
            }
            file.close();
        } catch (const std::exception& e) {
            std::cout << "Error reading file: " << e.what() << "\n";
            return 1;
        }

    } catch (const std::exception& e) {
        std::cout << "Error: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
