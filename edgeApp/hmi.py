import sys
import requests

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QProgressBar,
    QFrame
)

from PyQt5.QtCore import QTimer, Qt


class Dashboard(QWidget):

    def create_card(self, title, value="--"):

        card = QFrame()

        card.setStyleSheet("""
        QFrame{
            background-color:#10243C;
            border:2px solid cyan;
            border-radius:15px;
        }
        """)

        layout = QVBoxLayout()

        title_lbl = QLabel(title)
        title_lbl.setAlignment(Qt.AlignCenter)

        title_lbl.setStyleSheet("""
        border:0px;
        background:transparent;
        color:#00F7FF;
        font-size:14px;
        """)

        value_lbl = QLabel(value)

        value_lbl.setAlignment(Qt.AlignCenter)

        value_lbl.setStyleSheet("""
        border:0px;
        background:transparent;
        color:white;
        font-size:28px;
        font-weight:bold;
        """)

        layout.addWidget(title_lbl)
        layout.addWidget(value_lbl)

        card.setLayout(layout)

        return card, value_lbl

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Software Defined Vehicle Dashboard"
        )

        self.resize(1400, 850)

        self.setStyleSheet("""
        QWidget {
            background-color:#050A15;
            color:#00F7FF;
            font-family:Segoe UI;
        }

        QLabel {
            color:#00F7FF;
        }

        QProgressBar {
            border:2px solid cyan;
            border-radius:15px;
            text-align:center;
            height:35px;
            font-size:18px;
            color:white;
        }

        QProgressBar::chunk{
            background:#00FF88;
            border-radius:12px;
        }
        """)

        main_layout = QVBoxLayout()

        # ====================================
        # TITLE
        # ====================================

        title = QLabel(
            "SOFTWARE DEFINED VEHICLE CLOUD DASHBOARD"
        )

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
        font-size:34px;
        font-weight:bold;
        color:#00F7FF;
        margin:10px;
        """)

        main_layout.addWidget(title)

        # ====================================
        # KPI CARDS
        # ====================================

        kpi_layout = QHBoxLayout()

        speed_card, self.speed_value = self.create_card(
            "SPEED",
            "0"
        )

        soc_card, self.soc_value = self.create_card(
            "SOC",
            "0%"
        )

        temp_card, self.temp_value = self.create_card(
            "TEMP",
            "0°C"
        )

        alert_card, self.alert_count = self.create_card(
            "ALERTS",
            "0"
        )

        kpi_layout.addWidget(speed_card)
        kpi_layout.addWidget(soc_card)
        kpi_layout.addWidget(temp_card)
        kpi_layout.addWidget(alert_card)

        main_layout.addLayout(kpi_layout)

        # ====================================
        # VEHICLE PANEL
        # ====================================

        self.vehicle_visual = QLabel("""
   SOFTWARE DEFINED VEHICLE DASHBOARD
        """)

        self.vehicle_visual.setAlignment(
            Qt.AlignCenter
        )

        self.vehicle_visual.setStyleSheet("""
        background:#08111f;
        border:2px solid cyan;
        border-radius:20px;
        padding:20px;
        font-size:18px;
        font-weight:bold;
        """)

        main_layout.addWidget(
            self.vehicle_visual
        )

        # ====================================
        # STATUS TILES
        # ====================================

        status_layout = QHBoxLayout()

        self.battery = QLabel(
            "BATTERY\nHEALTHY"
        )

        self.driver = QLabel(
            "DRIVER\nALERT"
        )

        self.cloud = QLabel(
            "CLOUD\nCONNECTED"
        )

        self.bms = QLabel(
            "BMS\nENABLED"
        )

        self.dms = QLabel(
            "DMS\nENABLED"
        )

        for widget in [
            self.battery,
            self.driver,
            self.cloud,
            self.bms,
            self.dms
        ]:

            widget.setAlignment(Qt.AlignCenter)

            widget.setStyleSheet("""
            background:#10243C;
            border:2px solid #00FF88;
            border-radius:20px;
            color:#00FF88;
            font-size:18px;
            font-weight:bold;
            padding:20px;
            """)

            status_layout.addWidget(widget)

        main_layout.addLayout(
            status_layout
        )

        # ====================================
        # SOC SECTION
        # ====================================

        soc_title = QLabel(
            "BATTERY STATE OF CHARGE"
        )

        soc_title.setAlignment(Qt.AlignCenter)

        soc_title.setStyleSheet("""
        font-size:22px;
        font-weight:bold;
        """)

        main_layout.addWidget(
            soc_title
        )

        self.bar = QProgressBar()

        self.bar.setMinimum(0)
        self.bar.setMaximum(100)

        main_layout.addWidget(
            self.bar
        )

        # ====================================
        # VEHICLE DETAILS
        # ====================================

        self.details = QLabel(
            "Vehicle Details"
        )

        self.details.setAlignment(
            Qt.AlignCenter
        )

        self.details.setStyleSheet("""
        background:#08111f;
        border:2px solid cyan;
        border-radius:15px;
        padding:15px;
        font-size:18px;
        """)

        main_layout.addWidget(
            self.details
        )

        # ====================================
        # ALERT BANNER
        # ====================================

        self.alerts = QLabel(
            "SYSTEM HEALTHY"
        )

        self.alerts.setAlignment(
            Qt.AlignCenter
        )

        self.alerts.setStyleSheet("""
        background:#10243C;
        border:2px solid #00FF88;
        border-radius:15px;
        color:#00FF88;
        font-size:28px;
        font-weight:bold;
        padding:20px;
        """)

        main_layout.addWidget(
            self.alerts
        )

        self.setLayout(main_layout)

        self.timer = QTimer()

        self.timer.timeout.connect(
            self.refresh
        )

        self.timer.start(2000)

        self.refresh()

    def refresh(self):

        try:

            data = requests.get(
                "http://127.0.0.1:5000/latest_data"
            ).json()

            # KPI VALUES

            self.speed_value.setText(
                f"{int(data['speed'])} km/h"
            )

            self.soc_value.setText(
                f"{int(data['soc'])}%"
            )

            self.temp_value.setText(
                f"{int(data['temperature'])}°C"
            )

            self.bar.setValue(
                int(data["soc"])
            )

            self.details.setText(
                f"""
Vehicle : {data['vehicle_id']}

RPM : {int(data['rpm'])}

Voltage : {data['voltage']} V

Timestamp :
{data['timestamp']}
                """
            )

            # BATTERY

            if data["battery_health"] == "CRITICAL":

                self.battery.setText(
                    "BATTERY\nCRITICAL"
                )

                self.battery.setStyleSheet("""
                background:#330000;
                border:2px solid red;
                border-radius:20px;
                color:red;
                font-size:18px;
                font-weight:bold;
                padding:20px;
                """)

            else:

                self.battery.setText(
                    "BATTERY\nHEALTHY"
                )

            # DRIVER

            if data["driver_status"] == "DROWSY":

                self.driver.setText(
                    "DRIVER\nDROWSY"
                )

                self.driver.setStyleSheet("""
                background:#330000;
                border:2px solid red;
                border-radius:20px;
                color:red;
                font-size:18px;
                font-weight:bold;
                padding:20px;
                """)

            else:

                self.driver.setText(
                    "DRIVER\nALERT"
                )

            # BMS

            if data["bms_enabled"] == 1:

                self.bms.setText(
                    "BMS\nENABLED"
                )

            else:

                self.bms.setText(
                    "BMS\nDISABLED"
                )

            # DMS

            if data["dms_enabled"] == 1:

                self.dms.setText(
                    "DMS\nENABLED"
                )

            else:

                self.dms.setText(
                    "DMS\nDISABLED"
                )

            # ALERTS

            alert_data = requests.get(
                "http://127.0.0.1:5000/latest_alerts"
            ).json()

            self.alert_count.setText(
                str(
                    len(alert_data["alerts"])
                )
            )

            if alert_data["alerts"]:

                self.alerts.setText(
                    " | ".join(
                        alert_data["alerts"]
                    )
                )

                self.alerts.setStyleSheet("""
                background:#330000;
                border:2px solid red;
                border-radius:15px;
                color:red;
                font-size:26px;
                font-weight:bold;
                padding:20px;
                """)

            else:

                self.alerts.setText(
                    "SYSTEM HEALTHY"
                )

                self.alerts.setStyleSheet("""
                background:#10243C;
                border:2px solid #00FF88;
                border-radius:15px;
                color:#00FF88;
                font-size:26px;
                font-weight:bold;
                padding:20px;
                """)

        except Exception as e:

            self.cloud.setText(
                "CLOUD\nOFFLINE"
            )

            self.alerts.setText(
                f"ERROR : {e}"
            )


app = QApplication(sys.argv)

window = Dashboard()
window.show()

sys.exit(app.exec_())