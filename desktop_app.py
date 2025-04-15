import sys
import os
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QComboBox, 
                            QTableWidget, QTableWidgetItem, QHeaderView, 
                            QMessageBox, QTabWidget, QLineEdit, QFormLayout,
                            QDateEdit, QCheckBox, QGroupBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QIcon

# تكوين قاعدة البيانات
DB_PATH = 'app.db'

class AreaManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Area Manager")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("font-family: 'Cairo', 'Arial'; direction: rtl;")
        
        # إنشاء علامات التبويب
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # إضافة علامات التبويب
        self.setup_dashboard_tab()
        self.setup_clubs_tab()
        self.setup_facilities_tab()
        self.setup_checks_tab()
        
        self.load_data()
        
    def setup_dashboard_tab(self):
        dashboard = QWidget()
        layout = QVBoxLayout()
        
        # عنوان
        title = QLabel("لوحة التحكم")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # إحصائيات
        stats_layout = QHBoxLayout()
        
        # إحصائيات النوادي
        clubs_stats = QGroupBox("النوادي")
        clubs_stats_layout = QVBoxLayout()
        clubs_count = QLabel("عدد النوادي: 0")
        clubs_stats_layout.addWidget(clubs_count)
        clubs_stats.setLayout(clubs_stats_layout)
        stats_layout.addWidget(clubs_stats)
        
        # إحصائيات الفحوصات
        checks_stats = QGroupBox("الفحوصات")
        checks_stats_layout = QVBoxLayout()
        checks_count = QLabel("عدد الفحوصات: 0")
        checks_stats_layout.addWidget(checks_count)
        checks_stats.setLayout(checks_stats_layout)
        stats_layout.addWidget(checks_stats)
        
        layout.addLayout(stats_layout)
        
        dashboard.setLayout(layout)
        self.tabs.addTab(dashboard, "لوحة التحكم")
    
    def setup_clubs_tab(self):
        clubs = QWidget()
        layout = QVBoxLayout()
        
        # عنوان
        title = QLabel("النوادي")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # أزرار الإجراءات
        actions_layout = QHBoxLayout()
        add_club_btn = QPushButton("إضافة نادي جديد")
        add_club_btn.clicked.connect(self.add_club)
        actions_layout.addWidget(add_club_btn)
        layout.addLayout(actions_layout)
        
        # جدول النوادي
        self.clubs_table = QTableWidget()
        self.clubs_table.setColumnCount(5)
        self.clubs_table.setHorizontalHeaderLabels(["#", "اسم النادي", "المدير", "رقم الموظف", "الإجراءات"])
        self.clubs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.clubs_table)
        
        clubs.setLayout(layout)
        self.tabs.addTab(clubs, "النوادي")
    
    def setup_facilities_tab(self):
        facilities = QWidget()
        layout = QVBoxLayout()
        
        # عنوان
        title = QLabel("المرافق")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # اختيار النادي
        club_selection = QHBoxLayout()
        club_label = QLabel("النادي:")
        self.club_combo = QComboBox()
        club_selection.addWidget(club_label)
        club_selection.addWidget(self.club_combo)
        layout.addLayout(club_selection)
        
        # جدول المرافق
        self.facilities_table = QTableWidget()
        self.facilities_table.setColumnCount(4)
        self.facilities_table.setHorizontalHeaderLabels(["#", "اسم المرفق", "النوع", "الإجراءات"])
        self.facilities_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.facilities_table)
        
        facilities.setLayout(layout)
        self.tabs.addTab(facilities, "المرافق")
    
    def setup_checks_tab(self):
        checks = QWidget()
        layout = QVBoxLayout()
        
        # عنوان
        title = QLabel("سجل الفحوصات")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # جدول الفحوصات
        self.checks_table = QTableWidget()
        self.checks_table.setColumnCount(5)
        self.checks_table.setHorizontalHeaderLabels(["#", "النادي", "تاريخ الفحص", "النتيجة", "الإجراءات"])
        self.checks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.checks_table)
        
        checks.setLayout(layout)
        self.tabs.addTab(checks, "سجل الفحوصات")
    
    def load_data(self):
        try:
            # التحقق من وجود قاعدة البيانات
            if not os.path.exists(DB_PATH):
                QMessageBox.warning(self, "خطأ", "لم يتم العثور على قاعدة البيانات!")
                return
            
            # تحميل بيانات النوادي
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # تحميل النوادي
            cursor.execute("SELECT id, name, manager_name, employee_id FROM club")
            clubs = cursor.fetchall()
            
            self.clubs_table.setRowCount(len(clubs))
            for i, club in enumerate(clubs):
                self.clubs_table.setItem(i, 0, QTableWidgetItem(str(i+1)))
                self.clubs_table.setItem(i, 1, QTableWidgetItem(club[1]))
                self.clubs_table.setItem(i, 2, QTableWidgetItem(club[2]))
                self.clubs_table.setItem(i, 3, QTableWidgetItem(club[3]))
                
                # زر الإجراءات
                actions_widget = QWidget()
                actions_layout = QHBoxLayout()
                actions_layout.setContentsMargins(0, 0, 0, 0)
                
                view_btn = QPushButton("عرض")
                view_btn.clicked.connect(lambda _, club_id=club[0]: self.view_club(club_id))
                actions_layout.addWidget(view_btn)
                
                edit_btn = QPushButton("تعديل")
                edit_btn.clicked.connect(lambda _, club_id=club[0]: self.edit_club(club_id))
                actions_layout.addWidget(edit_btn)
                
                actions_widget.setLayout(actions_layout)
                self.clubs_table.setCellWidget(i, 4, actions_widget)
            
            # تحميل النوادي في القائمة المنسدلة
            self.club_combo.clear()
            self.club_combo.addItem("اختر النادي...", None)
            for club in clubs:
                self.club_combo.addItem(club[1], club[0])
            
            conn.close()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحميل البيانات: {str(e)}")
    
    def add_club(self):
        QMessageBox.information(self, "إضافة نادي", "سيتم إضافة هذه الميزة قريباً!")
    
    def view_club(self, club_id):
        QMessageBox.information(self, "عرض النادي", f"سيتم عرض النادي رقم {club_id} قريباً!")
    
    def edit_club(self, club_id):
        QMessageBox.information(self, "تعديل النادي", f"سيتم تعديل النادي رقم {club_id} قريباً!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AreaManagerApp()
    window.show()
    sys.exit(app.exec_())
