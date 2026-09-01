#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <thread>
#include <chrono>

std::vector<std::string> loadCsvRows(const std::string &path) {
    std::vector<std::string> rows;
    std::ifstream file(path);
    if (!file.is_open()) {
        std::cerr << "ERROR: Could not open file: " << path << "\n";
        return rows;
    }
    std::string line;
    std::getline(file, line); // skip header row
    while (std::getline(file, line)) {
        rows.push_back(line);
    }
    return rows;
}

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <csv_file> [delay_ms]\n";
        std::cerr << "Example: " << argv[0] << " data/Processed/B0005.csv 500\n";
        return 1;
    }

    std::string csvPath = argv[1];
    int delayMs = 500; // default: 500ms between rows
    if (argc >= 3) {
        delayMs = std::stoi(argv[2]);
    }

    auto rows = loadCsvRows(csvPath);
    if (rows.empty()) {
        std::cerr << "No data loaded. Exiting.\n";
        return 1;
    }

    std::cout << "Loaded " << rows.size() << " rows from " << csvPath << "\n";
    std::cout << "Simulating live stream with " << delayMs << "ms delay between rows...\n";
    std::cout << "Press Ctrl+C to stop early.\n\n";

    int count = 0;
    for (const auto &row : rows) {
        std::cout << "[LIVE] " << row << "\n";
        count++;
        std::this_thread::sleep_for(std::chrono::milliseconds(delayMs));
    }

    std::cout << "\nStream complete. Total rows sent: " << count << "\n";
    return 0;
}