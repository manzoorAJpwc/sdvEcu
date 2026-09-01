#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <filesystem>
#include <cmath>
#include <deque>

namespace fs = std::filesystem;

struct ThermalThresholds {
    double warningTemp = 45.0;
    double criticalTemp = 60.0;
};

struct HealthThresholds {
    double powerRestrictedSOH = 80.0;
    double criticalSOH = 65.0;
};

struct Row {
    int cycleIndex;
    std::string type;
    double voltage;
    double current;
    double temperature;
    double time;
    double capacity;
};

struct BatteryStatus {
    std::string batteryId;
    int cycleIndex;

    double soc_percent;
    double soh_percent;
    double temperature_C;
    std::string thermalStatus;
    int rul_cycles_remaining;

    bool isPowerRestricted;
    bool isCritical;
    std::string overallHealth;
};

std::vector<Row> loadCsvRows(const std::string &path) {
    std::vector<Row> rows;
    std::ifstream file(path);
    if (!file.is_open()) return rows;

    std::string line;
    std::getline(file, line);

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
        r.voltage = std::stod(voltage);
        r.current = std::stod(current);
        r.temperature = std::stod(temp);
        r.time = std::stod(time);
        r.capacity = std::stod(capacityStr);
        rows.push_back(r);
    }
    return rows;
}

std::string getThermalStatus(double temp, const ThermalThresholds &t) {
    if (temp < 0) return "Too Cold";
    if (temp <= t.warningTemp) return "Normal";
    if (temp <= t.criticalTemp) return "Warning";
    return "Critical Overheat";
}

std::string getOverallHealth(double soh, const std::string &thermal, bool isCritical,
                              const HealthThresholds &h) {
    if (isCritical || thermal == "Critical Overheat") return "Critical";
    if (soh < 70.0 || thermal == "Warning")            return "Poor";
    if (soh < h.powerRestrictedSOH)                     return "Degraded";
    return "Good";
}

class BMSStatusService {
private:
    std::string batteryId;
    double ratedCapacity;
    std::vector<BatteryStatus> statusHistory;
    std::deque<std::pair<int, double>> sohWindow;
    static const size_t WINDOW_SIZE = 50;
    ThermalThresholds thermalConfig;
    HealthThresholds healthConfig;

public:
    BMSStatusService(const std::string &id,
                      ThermalThresholds tConfig = ThermalThresholds(),
                      HealthThresholds hConfig = HealthThresholds())
        : batteryId(id), ratedCapacity(-1.0),
          thermalConfig(tConfig), healthConfig(hConfig) {}

    BatteryStatus evaluate(int cycleIndex, double capacity, double avgTemp, double socEstimate) {
        if (ratedCapacity < 0) {
            ratedCapacity = capacity;
        }

        double soh = (capacity / ratedCapacity) * 100.0;

        BatteryStatus status;
        status.batteryId = batteryId;
        status.cycleIndex = cycleIndex;
        status.soc_percent = socEstimate;
        status.soh_percent = soh;
        status.temperature_C = avgTemp;
        status.thermalStatus = getThermalStatus(avgTemp, thermalConfig);
        status.isPowerRestricted = (soh < healthConfig.powerRestrictedSOH);
        status.isCritical = (soh < healthConfig.criticalSOH);

        sohWindow.push_back({cycleIndex, soh});
        if (sohWindow.size() > WINDOW_SIZE) {
            sohWindow.pop_front();
        }

        const double MIN_MEANINGFUL_DEGRADATION = 0.5; // require at least 0.5% SOH drop across window
        const int MAX_REASONABLE_RUL = 1000;            // sanity cap

        if (sohWindow.size() >= 2 && soh < 100.0) {
            int cycleSpan = sohWindow.back().first - sohWindow.front().first;
            double sohSpan = sohWindow.front().second - sohWindow.back().second;

            if (cycleSpan > 0 && sohSpan > MIN_MEANINGFUL_DEGRADATION) {
                double recentDegradationRate = sohSpan / cycleSpan;
                double sohRemainingToThreshold = soh - healthConfig.powerRestrictedSOH;
                int calculatedRul = (sohRemainingToThreshold > 0)
                    ? static_cast<int>(sohRemainingToThreshold / recentDegradationRate)
                    : 0;
                status.rul_cycles_remaining = std::min(calculatedRul, MAX_REASONABLE_RUL);
            } else {
                status.rul_cycles_remaining = -1;
            }
        } else {
            status.rul_cycles_remaining = -1;
        }

        status.overallHealth = getOverallHealth(soh, status.thermalStatus, status.isCritical, healthConfig);

        statusHistory.push_back(status);
        return status;
    }

    void exportHistoryToCsv(const std::string &outPath) const {
        std::ofstream out(outPath);
        out << "battery_id,cycle_index,soc_percent,soh_percent,temperature_C,"
               "thermal_status,rul_cycles_remaining,is_power_restricted,"
               "is_critical,overall_health\n";
        for (const auto &s : statusHistory) {
            out << s.batteryId << "," << s.cycleIndex << "," << s.soc_percent << ","
                << s.soh_percent << "," << s.temperature_C << "," << s.thermalStatus << ","
                << s.rul_cycles_remaining << "," << (s.isPowerRestricted ? 1 : 0) << ","
                << (s.isCritical ? 1 : 0) << "," << s.overallHealth << "\n";
        }
        out.close();
    }

    void exportHistoryToJson(const std::string &outPath) const {
        std::ofstream out(outPath);
        out << "[\n";
        for (size_t i = 0; i < statusHistory.size(); i++) {
            const auto &s = statusHistory[i];
            out << "  {\n"
                << "    \"battery_id\": \"" << s.batteryId << "\",\n"
                << "    \"cycle_index\": " << s.cycleIndex << ",\n"
                << "    \"soc_percent\": " << s.soc_percent << ",\n"
                << "    \"soh_percent\": " << s.soh_percent << ",\n"
                << "    \"temperature_C\": " << s.temperature_C << ",\n"
                << "    \"thermal_status\": \"" << s.thermalStatus << "\",\n"
                << "    \"rul_cycles_remaining\": " << s.rul_cycles_remaining << ",\n"
                << "    \"is_power_restricted\": " << (s.isPowerRestricted ? "true" : "false") << ",\n"
                << "    \"is_critical\": " << (s.isCritical ? "true" : "false") << ",\n"
                << "    \"overall_health\": \"" << s.overallHealth << "\"\n"
                << "  }" << (i < statusHistory.size()-1 ? "," : "") << "\n";
        }
        out << "]\n";
        out.close();
    }

    const std::vector<BatteryStatus>& getHistory() const { return statusHistory; }
};

void processFile(const std::string &csvPath, const std::string &batteryId) {
    std::cout << "\n--- Processing: " << batteryId << " ---\n";
    auto rows = loadCsvRows(csvPath);
    if (rows.empty()) {
        std::cerr << "No data loaded.\n";
        return;
    }

    BMSStatusService service(batteryId);

    int currentCycle = -1;
    std::string currentType = "";
    double tempSum = 0; int tempCount = 0;
    double cycleCapacity = 0;

    double runningSOC = 100.0;
    double lastCompletedCycleSOC = 100.0;
    double lastTime = 0.0;
    bool firstRowOfCycle = true;
    double socAtCycleStart = 100.0;
    double ratedCapacity_Ah = -1.0;

    for (size_t i = 0; i < rows.size(); i++) {
        const Row &r = rows[i];
        bool isNewCycle = (r.cycleIndex != currentCycle);

        if (isNewCycle) {
            if (currentCycle != -1 && currentType == "discharge" && tempCount > 0) {
                double avgTemp = tempSum / tempCount;
                service.evaluate(currentCycle, cycleCapacity, avgTemp, socAtCycleStart);
                lastCompletedCycleSOC = runningSOC;
            }

            currentCycle = r.cycleIndex;
            currentType = r.type;
            tempSum = 0;
            tempCount = 0;
            cycleCapacity = r.capacity;
            firstRowOfCycle = true;
            runningSOC = 100.0;
        }

        if (r.type == "discharge") {
            if (ratedCapacity_Ah < 0) {
                ratedCapacity_Ah = r.capacity > 0 ? r.capacity : 1.85;
            }

            if (firstRowOfCycle) {
                socAtCycleStart = 100.0;
                lastTime = r.time;
                firstRowOfCycle = false;
            } else {
                double dt = r.time - lastTime;
                if (dt > 0) {
                    double ratedCapacity_As = ratedCapacity_Ah * 3600.0;
                    double chargeUsed = std::abs(r.current) * dt;
                    runningSOC -= (chargeUsed / ratedCapacity_As) * 100.0;
                    runningSOC = std::max(0.0, std::min(100.0, runningSOC));
                }
                lastTime = r.time;
            }

            tempSum += r.temperature;
            tempCount++;
            cycleCapacity = r.capacity;
        }
    }

    if (currentType == "discharge" && tempCount > 0) {
        double avgTemp = tempSum / tempCount;
        service.evaluate(currentCycle, cycleCapacity, avgTemp, socAtCycleStart);
        lastCompletedCycleSOC = runningSOC;
    }

    const auto &history = service.getHistory();
    if (history.empty()) {
        std::cerr << "No discharge cycles evaluated.\n";
        return;
    }

    int restrictedCount = 0, criticalCount = 0;
    for (const auto &s : history) {
        if (s.isPowerRestricted) restrictedCount++;
        if (s.isCritical) criticalCount++;
    }

    const auto &last = history.back();
    std::cout << "Total discharge cycles evaluated: " << history.size() << "\n";
    std::cout << "Final Cycle " << last.cycleIndex
               << " | SOC: " << last.soc_percent << "%"
               << " | SOH: " << last.soh_percent << "%"
               << " | Temp: " << last.temperature_C << "C (" << last.thermalStatus << ")"
               << " | RUL: " << last.rul_cycles_remaining << " cycles"
               << " | Overall: " << last.overallHealth << "\n";
    std::cout << "Final discharge cycle ending SOC (Coulomb count): "
               << lastCompletedCycleSOC << "%\n";
    std::cout << "Cycles PowerRestricted: " << restrictedCount
               << " | Critical: " << criticalCount << "\n";

    std::string outPath = csvPath.substr(0, csvPath.find_last_of('.')) + "_status.csv";
    service.exportHistoryToCsv(outPath);
    std::cout << "Saved: " << outPath << "\n";

    std::string jsonPath = csvPath.substr(0, csvPath.find_last_of('.')) + "_status.json";
    service.exportHistoryToJson(jsonPath);
    std::cout << "Saved: " << jsonPath << "\n";
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
            std::string batteryId = entry.path().stem().string();
            processFile(path, batteryId);
            count++;
        }
    }

    std::cout << "\n=== Done. Processed " << count << " battery files. ===\n";
    return 0;
}