#include <iostream>
#include <string>
#include <cstdlib>
#include <limits>

void runBMS() {
    std::cout << "\n--- Launching Battery Health Service ---\n";
    int exitCode = system("cd ..\\bmsApp && bms_status_service.exe");
    std::cout << "BMS finished with exit code: " << exitCode << "\n";
}

void runDMS() {
    std::cout << "\n--- Launching DMS (Driver Monitoring System) ---\n";
    int exitCode = system("cd ..\\adas && dms_harr.exe");
    std::cout << "DMS finished with exit code: " << exitCode << "\n";
}

void runFCW() {
    std::cout << "\n--- Launching FCW (Forward Collision Warning) ---\n";
    int exitCode = system("cd ..\\adas && fcw_object.exe");
    std::cout << "FCW finished with exit code: " << exitCode << "\n";
}

void runLDW() {
    std::cout << "\n--- Launching LDW (Lane Departure Warning) ---\n";
    int exitCode = system("cd ..\\adas && ldw_camera.exe");
    std::cout << "LDW finished with exit code: " << exitCode << "\n";
}

void showMenu() {
    std::cout << "\n=========================================\n";
    std::cout << "   SDV System Orchestrator\n";
    std::cout << "=========================================\n";
    std::cout << "1. Run Battery Health Service (BMS)\n";
    std::cout << "2. Run Driver Monitoring System (DMS)\n";
    std::cout << "3. Run Forward Collision Warning (FCW)\n";
    std::cout << "4. Run Lane Departure Warning (LDW)\n";
    std::cout << "5. Run ALL (sequentially)\n";
    std::cout << "0. Exit\n";
    std::cout << "=========================================\n";
    std::cout << "Enter your choice: ";
}

int main() {
    int choice;
    bool running = true;

    while (running) {
        showMenu();
        std::cin >> choice;

        if (std::cin.fail()) {
            std::cin.clear();
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
            std::cout << "Invalid input. Please enter a number.\n";
            continue;
        }

        switch (choice) {
            case 1: runBMS(); break;
            case 2: runDMS(); break;
            case 3: runFCW(); break;
            case 4: runLDW(); break;
            case 5:
                runBMS(); runDMS(); runFCW(); runLDW();
                break;
            case 0:
                std::cout << "Exiting orchestrator. Goodbye!\n";
                running = false;
                break;
            default:
                std::cout << "Invalid choice. Please select 0-5.\n";
        }
    }

    return 0;
}