#include <matio.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <filesystem>

namespace fs = std::filesystem;

std::vector<double> getDoubleVector(matvar_t *var) {
    std::vector<double> result;
    if (!var || var->data_type != MAT_T_DOUBLE) return result;
    size_t n = 1;
    for (int i = 0; i < var->rank; i++) n *= var->dims[i];
    double *data = static_cast<double*>(var->data);
    result.assign(data, data + n);
    return result;
}

double getScalar(matvar_t *var) {
    auto v = getDoubleVector(var);
    return v.empty() ? 0.0 : v[0];
}

std::string getString(matvar_t *var) {
    if (!var || var->class_type != MAT_C_CHAR) return "";
    size_t n = 1;
    for (int i = 0; i < var->rank; i++) n *= var->dims[i];
    std::string s;
    if (var->data_size == 1) {
        char *data = static_cast<char*>(var->data);
        s.assign(data, n);
    } else {
        mat_uint16_t *data = static_cast<mat_uint16_t*>(var->data);
        for (size_t i = 0; i < n; i++) s += static_cast<char>(data[i]);
    }
    return s;
}

bool convertMatToCsv(const std::string &matPath, const std::string &csvPath) {
    mat_t *matfp = Mat_Open(matPath.c_str(), MAT_ACC_RDONLY);
    if (!matfp) {
        std::cerr << "  ERROR: Cannot open " << matPath << "\n";
        return false;
    }

    matvar_t *topVar = nullptr;
    matvar_t *var;
    while ((var = Mat_VarReadNextInfo(matfp)) != nullptr) {
        if (var->class_type == MAT_C_STRUCT) {
            Mat_VarReadDataAll(matfp, var);
            topVar = var;
            break;
        }
        Mat_VarFree(var);
    }

    if (!topVar) {
        std::cerr << "  ERROR: No struct found in " << matPath << "\n";
        Mat_Close(matfp);
        return false;
    }

    matvar_t *cycleArr = Mat_VarGetStructFieldByName(topVar, "cycle", 0);
    if (!cycleArr) {
        std::cerr << "  ERROR: No 'cycle' field in " << matPath << "\n";
        Mat_VarFree(topVar);
        Mat_Close(matfp);
        return false;
    }

    size_t numCycles = cycleArr->dims[0] * cycleArr->dims[1];
    std::cout << "  Cycles found: " << numCycles << "\n";

    std::ofstream csv(csvPath);
    csv << "cycle_index,type,ambient_temperature,sample_index,"
           "Voltage_measured,Current_measured,Temperature_measured,"
           "Current_load_or_charge,Voltage_load_or_charge,Time,Capacity\n";

    for (size_t c = 0; c < numCycles; c++) {
        std::string type = getString(Mat_VarGetStructFieldByName(cycleArr, "type", c));
        double ambTemp = getScalar(Mat_VarGetStructFieldByName(cycleArr, "ambient_temperature", c));
        matvar_t *dataVar = Mat_VarGetStructFieldByName(cycleArr, "data", c);
        if (!dataVar) continue;

        auto voltage = getDoubleVector(Mat_VarGetStructFieldByName(dataVar, "Voltage_measured", 0));
        auto current = getDoubleVector(Mat_VarGetStructFieldByName(dataVar, "Current_measured", 0));
        auto temp    = getDoubleVector(Mat_VarGetStructFieldByName(dataVar, "Temperature_measured", 0));
        auto time    = getDoubleVector(Mat_VarGetStructFieldByName(dataVar, "Time", 0));
        auto capVec  = getDoubleVector(Mat_VarGetStructFieldByName(dataVar, "Capacity", 0));

        matvar_t *loadCurVar = Mat_VarGetStructFieldByName(dataVar, "Current_load", 0);
        if (!loadCurVar) loadCurVar = Mat_VarGetStructFieldByName(dataVar, "Current_charge", 0);
        auto loadCurrent = getDoubleVector(loadCurVar);

        matvar_t *loadVoltVar = Mat_VarGetStructFieldByName(dataVar, "Voltage_load", 0);
        if (!loadVoltVar) loadVoltVar = Mat_VarGetStructFieldByName(dataVar, "Voltage_charge", 0);
        auto loadVoltage = getDoubleVector(loadVoltVar);

        double capVal = capVec.empty() ? 0.0 : capVec[0];
        size_t n = voltage.size();

        for (size_t i = 0; i < n; i++) {
            csv << c << "," << type << "," << ambTemp << "," << i << ","
                << (i < voltage.size() ? voltage[i] : 0) << ","
                << (i < current.size() ? current[i] : 0) << ","
                << (i < temp.size() ? temp[i] : 0) << ","
                << (i < loadCurrent.size() ? loadCurrent[i] : 0) << ","
                << (i < loadVoltage.size() ? loadVoltage[i] : 0) << ","
                << (i < time.size() ? time[i] : 0) << ","
                << capVal << "\n";
        }
    }

    csv.close();
    Mat_VarFree(topVar);
    Mat_Close(matfp);
    return true;
}

int main(int argc, char** argv) {
    std::string inputDir = "data/Raw/nasa_battery_source";
    std::string outputDir = "data/Processed";

    if (argc >= 2) inputDir = argv[1];
    if (argc >= 3) outputDir = argv[2];

    if (!fs::exists(outputDir)) {
        fs::create_directories(outputDir);
        std::cout << "Created output directory: " << outputDir << "\n";
    }

    int successCount = 0, failCount = 0;

    for (const auto &entry : fs::directory_iterator(inputDir)) {
        if (entry.path().extension() == ".mat") {
            std::string matPath = entry.path().string();
            std::string stem = entry.path().stem().string();
            std::string csvPath = outputDir + "/" + stem + ".csv";

            std::cout << "Converting: " << matPath << " -> " << csvPath << "\n";
            if (convertMatToCsv(matPath, csvPath)) {
                std::cout << "  Success.\n";
                successCount++;
            } else {
                std::cout << "  Failed.\n";
                failCount++;
            }
        }
    }

    std::cout << "\n=== Summary ===\n";
    std::cout << "Converted: " << successCount << "\n";
    std::cout << "Failed:    " << failCount << "\n";

    return 0;
}