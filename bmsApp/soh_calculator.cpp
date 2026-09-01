#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <filesystem>

namespace fs = std::filesystem;

struct DischargeRecord {
    int cycleIndex;
    double capacity;
};

std::vector<DischargeRecord> extractDischargeCapacities(const std::string &csvPath) {
    std::vector<DischargeRecord> records;
    std::ifstream file(csvPath);
    if (!file.is_open()) return records;

    std::string line;
    std::getline(file, line); // skip header
    int lastCycleSeen = -1;

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

        if (type != "discharge") continue;

        int cycleIndex = std::stoi(cycleStr);
        double capacity = std::stod(capacityStr);

        if (cycleIndex != lastCycleSeen) {
            records.push_back({cycleIndex, capacity});
            lastCycleSeen = cycleIndex;
        }
    }
    return records;
}

void processFile(const std::string &csvPath) {
    std::cout << "\n--- Processing: " << csvPath << " ---\n";
    auto records = extractDischargeCapacities(csvPath);

    if (records.empty()) {
        std::cerr << "No discharge records found in " << csvPath << "\n";
        return;
    }

    double ratedCapacity = records[0].capacity;
    std::cout << "Baseline capacity: " << ratedCapacity << " Ah\n";
    std::cout << "Total discharge cycles: " << records.size() << "\n";

    std::string outPath = csvPath.substr(0, csvPath.find_last_of('.')) + "_SOH.csv";
    std::ofstream out(outPath);
    out << "cycle_index,capacity_Ah,SOH_percent\n";

    for (const auto &rec : records) {
        double soh = (rec.capacity / ratedCapacity) * 100.0;
        out << rec.cycleIndex << "," << rec.capacity << "," << soh << "\n";
    }
    out.close();

    auto &last = records.back();
    double lastSoh = (last.capacity / ratedCapacity) * 100.0;
    std::cout << "Final cycle " << last.cycleIndex << " -> SOH: " << lastSoh << "%\n";
    std::cout << "Saved: " << outPath << "\n";
}

int main(int argc, char** argv) {
    std::string inputDir = "data/Processed";
    if (argc >= 2) inputDir = argv[1];

    int count = 0;
    for (const auto &entry : fs::directory_iterator(inputDir)) {
        std::string path = entry.path().string();
        // Only process base battery CSVs, skip already-generated _SOH/_status files
        if (entry.path().extension() == ".csv" &&
            path.find("_SOH") == std::string::npos &&
            path.find("_status") == std::string::npos) {
            processFile(path);
            count++;
        }
    }

    std::cout << "\n=== Done. Processed " << count << " battery files. ===\n";
    return 0;
}