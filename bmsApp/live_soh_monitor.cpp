#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <filesystem>

namespace fs = std::filesystem;

struct Row {
    int cycleIndex;
    std::string type;
    double capacity;
};

std::vector<Row> loadCsvRows(const std::string &path) {
    std::vector<Row> rows;
    std::ifstream file(path);
    if (!file.is_open()) return rows;

    std::string line;
    std::getline(file, line); // skip header

    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string cycleStr, type, ambTemp, sampleIdx, voltage, current,
                    temp, loadCurrent, loadVoltage, time, capacityStr;

        std::getline(ss, cycleStr, ',');
        std::getline(ss, type, ',');
        std::getline(ss, ambTemp, ',');
        std::getline(ss, sampleIdx, ',');
        std::getline(ss, voltage, ',');
        std::getline(ss, current, ',');
        std::getline(ss, temp, ',');
        std::getline(ss, loadCurrent, ',');
        std::getline(ss, loadVoltage, ',');
        std::getline(ss, time, ',');
        std::getline(ss, capacityStr, ',');

        Row r;
        r.cycleIndex = std::stoi(cycleStr);
        r.type = type;
        r.capacity = std::stod(capacityStr);
        rows.push_back(r);
    }
    return rows;
}

void processFile(const std::string &csvPath) {
    std::cout << "\n--- Monitoring: " << csvPath << " ---\n";
    auto rows = loadCsvRows(csvPath);
    if (rows.empty()) {
        std::cerr << "No data loaded.\n";
        return;
    }

    double ratedCapacity = -1.0;
    int lastCycleIndex = -1;
    int eventCount = 0, warningCount = 0;

    for (const auto &r : rows) {
        bool isNewCycle = (r.cycleIndex != lastCycleIndex);
        bool isDischarge = (r.type == "discharge");

        if (isNewCycle && isDischarge) {
            if (ratedCapacity < 0) {
                ratedCapacity = r.capacity;
            } else {
                double soh = (r.capacity / ratedCapacity) * 100.0;
                if (soh < 80.0) warningCount++;
            }
            eventCount++;
        }
        lastCycleIndex = r.cycleIndex;
    }

    std::cout << "Total discharge cycle events: " << eventCount << "\n";
    std::cout << "Total warnings triggered (SOH < 80%): " << warningCount << "\n";
}

int main(int argc, char** argv) {
    std::string inputDir = "data/Processed";
    if (argc >= 2) inputDir = argv[1];

    int count = 0;
    for (const auto &entry : fs::directory_iterator(inputDir)) {
        std::string path = entry.path().string();
        if (entry.path().extension() == ".csv" &&
            path.find("_SOH") == std::string::npos &&
            path.find("_status") == std::string::npos) {
            processFile(path);
            count++;
        }
    }

    std::cout << "\n=== Done. Monitored " << count << " battery files. ===\n";
    return 0;
}