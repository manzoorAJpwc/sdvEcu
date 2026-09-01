#include <matio.h>
#include <iostream>

void printFields(matvar_t *var, int indent = 0) {
    std::string pad(indent, ' ');
    if (!var) {
        std::cout << pad << "(null variable)\n";
        return;
    }
    std::cout << pad << "Name: " << (var->name ? var->name : "unnamed")
               << " | class_type: " << var->class_type
               << " | data_type: " << var->data_type
               << " | rank: " << var->rank << " | dims: ";
    for (int i = 0; i < var->rank; i++) std::cout << var->dims[i] << " ";
    std::cout << "\n";
}

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <file.mat>\n";
        return 1;
    }

    mat_t *matfp = Mat_Open(argv[1], MAT_ACC_RDONLY);
    if (!matfp) {
        std::cerr << "Cannot open " << argv[1] << "\n";
        return 1;
    }
    std::cout << "MAT file opened successfully.\n";

    matvar_t *topVar = Mat_VarRead(matfp, "B0005");
    if (!topVar) {
        std::cerr << "Could not read variable B0005\n";
        Mat_Close(matfp);
        return 1;
    }

    std::cout << "Top variable: " << topVar->name << "\n";
    printFields(topVar);

    matvar_t *cycleVar = Mat_VarGetStructFieldByName(topVar, "cycle", 0);
    if (!cycleVar) {
        std::cerr << "No 'cycle' field found.\n";
        Mat_VarFree(topVar);
        Mat_Close(matfp);
        return 1;
    }

    std::cout << "\n'cycle' field info:\n";
    printFields(cycleVar, 2);

    size_t numCycles = 1;
    for (int i = 0; i < cycleVar->rank; i++) numCycles *= cycleVar->dims[i];
    std::cout << "Number of cycle entries: " << numCycles << "\n";

    // Print fields of first cycle entry
    if (cycleVar->class_type == MAT_C_STRUCT && numCycles > 0) {
        std::cout << "\nFields inside cycle[0]:\n";
        int nFields = Mat_VarGetNumberOfFields(cycleVar);
        char * const *fieldNames = Mat_VarGetStructFieldnames(cycleVar);
        for (int i = 0; i < nFields; i++) {
            std::cout << "  - " << fieldNames[i] << "\n";
        }

        // Try to look inside 'data' field if it exists
        matvar_t *dataVar = Mat_VarGetStructFieldByName(cycleVar, "data", 0);
        if (dataVar) {
            std::cout << "\nFields inside cycle[0].data:\n";
            int nDataFields = Mat_VarGetNumberOfFields(dataVar);
            char * const *dataFieldNames = Mat_VarGetStructFieldnames(dataVar);
            for (int i = 0; i < nDataFields; i++) {
                std::cout << "  - " << dataFieldNames[i] << "\n";
            }
        } else {
            std::cout << "\nNo 'data' field found inside cycle[0].\n";
        }

        // Print 'type' if present
        matvar_t *typeVar = Mat_VarGetStructFieldByName(cycleVar, "type", 0);
        if (typeVar && typeVar->class_type == MAT_C_CHAR) {
            size_t n = 1;
            for (int i = 0; i < typeVar->rank; i++) n *= typeVar->dims[i];
            std::string s;
            if (typeVar->data_size == 1) {
                char *d = static_cast<char*>(typeVar->data);
                s.assign(d, n);
            } else {
                mat_uint16_t *d = static_cast<mat_uint16_t*>(typeVar->data);
                for (size_t i = 0; i < n; i++) s += (char)d[i];
            }
            std::cout << "\ncycle[0].type = \"" << s << "\"\n";
        }
    }

    Mat_VarFree(topVar);
    Mat_Close(matfp);
    return 0;
}