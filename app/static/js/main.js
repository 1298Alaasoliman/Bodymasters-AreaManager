// ملف JavaScript الرئيسي لنظام إدارة النوادي الرياضية

// تنفيذ الكود عند اكتمال تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // إخفاء رسائل التنبيه بعد 5 ثوانٍ
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // تفعيل tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // تفعيل popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // تفعيل تحقق النموذج
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // تفعيل تبديل حقول الإجازة
    const leaveCheckbox = document.getElementById('is_leave');
    const leaveTypeField = document.getElementById('leave_type_group');
    const timeInField = document.getElementById('time_in_group');
    const timeOutField = document.getElementById('time_out_group');

    if (leaveCheckbox && leaveTypeField && timeInField && timeOutField) {
        function toggleLeaveFields() {
            if (leaveCheckbox.checked) {
                leaveTypeField.style.display = 'block';
                timeInField.style.display = 'none';
                timeOutField.style.display = 'none';
            } else {
                leaveTypeField.style.display = 'none';
                timeInField.style.display = 'block';
                timeOutField.style.display = 'block';
            }
        }

        // تنفيذ الدالة عند تحميل الصفحة
        toggleLeaveFields();

        // تنفيذ الدالة عند تغيير حالة الاختيار
        leaveCheckbox.addEventListener('change', toggleLeaveFields);
    }

    // تفعيل البحث في الجداول
    const tableSearch = document.getElementById('tableSearch');
    if (tableSearch) {
        tableSearch.addEventListener('keyup', function() {
            const searchText = this.value.toLowerCase();
            const table = document.querySelector(this.dataset.table);
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(function(row) {
                const text = row.textContent.toLowerCase();
                if (text.indexOf(searchText) > -1) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // تفعيل البحث في جدول الموظفين في صفحة النادي
    const employeeSearch = document.getElementById('employeeSearch');
    const clearEmployeeSearch = document.getElementById('clearEmployeeSearch');
    if (employeeSearch) {
        employeeSearch.addEventListener('keyup', function() {
            const searchText = this.value.toLowerCase();
            const table = document.getElementById('clubEmployeesTable');
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(function(row) {
                const text = row.textContent.toLowerCase();
                if (text.indexOf(searchText) > -1) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });

        // مسح البحث
        if (clearEmployeeSearch) {
            clearEmployeeSearch.addEventListener('click', function() {
                employeeSearch.value = '';
                const table = document.getElementById('clubEmployeesTable');
                const rows = table.querySelectorAll('tbody tr');
                rows.forEach(function(row) {
                    row.style.display = '';
                });
            });
        }
    }

    // تفعيل الفلتر في رؤوس الأعمدة
    const filterIcons = document.querySelectorAll('.filter-icon i');
    if (filterIcons.length > 0) {
        // إنشاء قائمة الفلتر
        const filterDropdown = document.createElement('div');
        filterDropdown.className = 'filter-dropdown';
        filterDropdown.innerHTML = `
            <div class="filter-search">
                <input type="text" class="form-control form-control-sm" placeholder="بحث..." id="filterSearch">
            </div>
            <div class="filter-options"></div>
            <div class="filter-actions">
                <button class="btn btn-sm btn-primary" id="applyFilter">تطبيق</button>
                <button class="btn btn-sm btn-secondary" id="clearFilter">مسح</button>
            </div>
        `;
        document.body.appendChild(filterDropdown);

        // المتغيرات العامة للفلتر
        let activeFilterIcon = null;
        let activeColumn = null;
        let filterValues = {};

        // إغلاق الفلتر عند النقر خارجه
        document.addEventListener('click', function(e) {
            if (!filterDropdown.contains(e.target) &&
                !e.target.classList.contains('fa-filter') &&
                !e.target.closest('.filter-icon')) {
                filterDropdown.classList.remove('show');
                if (activeFilterIcon) {
                    activeFilterIcon.classList.remove('active');
                    activeFilterIcon = null;
                }
            }
        });

        // إظهار قائمة الفلتر عند النقر على أيقونة الفلتر
        filterIcons.forEach(function(icon) {
            icon.addEventListener('click', function(e) {
                e.stopPropagation();

                // إذا كانت القائمة مفتوحة بالفعل لنفس العمود، أغلقها
                if (activeFilterIcon === this && filterDropdown.classList.contains('show')) {
                    filterDropdown.classList.remove('show');
                    this.classList.remove('active');
                    activeFilterIcon = null;
                    return;
                }

                // إزالة التنشيط من الأيقونة السابقة
                if (activeFilterIcon) {
                    activeFilterIcon.classList.remove('active');
                }

                // تنشيط الأيقونة الحالية
                this.classList.add('active');
                activeFilterIcon = this;
                activeColumn = parseInt(this.dataset.column);

                // تحديد موقع القائمة
                const iconRect = this.getBoundingClientRect();
                filterDropdown.style.top = (iconRect.bottom + window.scrollY) + 'px';
                filterDropdown.style.left = (iconRect.left + window.scrollX - 100) + 'px';

                // جمع القيم الفريدة من العمود
                const table = document.getElementById('employeesTable');
                const rows = table.querySelectorAll('tbody tr');
                const uniqueValues = new Set();

                rows.forEach(function(row) {
                    const cell = row.cells[activeColumn];
                    if (cell) {
                        uniqueValues.add(cell.textContent.trim());
                    }
                });

                // إنشاء خيارات الفلتر
                const filterOptions = filterDropdown.querySelector('.filter-options');
                filterOptions.innerHTML = '';

                uniqueValues.forEach(function(value) {
                    if (value) {
                        const option = document.createElement('div');
                        option.className = 'filter-option';
                        const isChecked = filterValues[activeColumn] && filterValues[activeColumn].includes(value);
                        option.innerHTML = `
                            <input type="checkbox" value="${value}" ${isChecked ? 'checked' : ''}>
                            <span>${value}</span>
                        `;
                        filterOptions.appendChild(option);
                    }
                });

                // إظهار القائمة
                filterDropdown.classList.add('show');

                // تفعيل البحث في الفلتر
                const filterSearch = document.getElementById('filterSearch');
                filterSearch.value = '';
                filterSearch.focus();

                filterSearch.addEventListener('keyup', function() {
                    const searchText = this.value.toLowerCase();
                    const options = filterOptions.querySelectorAll('.filter-option');

                    options.forEach(function(option) {
                        const text = option.textContent.toLowerCase();
                        if (text.indexOf(searchText) > -1) {
                            option.style.display = '';
                        } else {
                            option.style.display = 'none';
                        }
                    });
                });
            });
        });

        // تطبيق الفلتر
        document.getElementById('applyFilter').addEventListener('click', function() {
            if (activeColumn !== null) {
                const checkedOptions = filterDropdown.querySelectorAll('.filter-options input:checked');
                const values = Array.from(checkedOptions).map(input => input.value);

                if (values.length > 0) {
                    filterValues[activeColumn] = values;
                    activeFilterIcon.classList.add('active');
                } else {
                    delete filterValues[activeColumn];
                    activeFilterIcon.classList.remove('active');
                }

                applyFilters();
                filterDropdown.classList.remove('show');
            }
        });

        // مسح الفلتر
        document.getElementById('clearFilter').addEventListener('click', function() {
            if (activeColumn !== null) {
                delete filterValues[activeColumn];
                activeFilterIcon.classList.remove('active');
                applyFilters();
                filterDropdown.classList.remove('show');
            }
        });

        // تطبيق جميع الفلاتر
        function applyFilters() {
            const table = document.getElementById('employeesTable');
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(function(row) {
                let display = true;

                for (const column in filterValues) {
                    const cell = row.cells[parseInt(column)];
                    const cellValue = cell ? cell.textContent.trim() : '';

                    if (!filterValues[column].includes(cellValue)) {
                        display = false;
                        break;
                    }
                }

                row.style.display = display ? '' : 'none';
            });
        }
    }

    // تفعيل تحديد/إلغاء تحديد الكل
    const selectAllCheckbox = document.getElementById('selectAll');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll(this.dataset.target);
            checkboxes.forEach(function(checkbox) {
                checkbox.checked = selectAllCheckbox.checked;
            });
        });
    }

    // تفعيل تحميل الصور المعاينة
    const imageUpload = document.getElementById('imageUpload');
    const imagePreview = document.getElementById('imagePreview');

    if (imageUpload && imagePreview) {
        imageUpload.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.addEventListener('load', function() {
                    imagePreview.src = reader.result;
                    imagePreview.style.display = 'block';
                });
                reader.readAsDataURL(file);
            }
        });
    }

    // تفعيل تنسيق التاريخ والوقت (بالتقويم الإنجليزي)
    const dateTimeElements = document.querySelectorAll('.format-datetime');
    dateTimeElements.forEach(function(element) {
        const dateTime = new Date(element.textContent);
        element.textContent = dateTime.toLocaleString('en-US', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });
    });

    const dateElements = document.querySelectorAll('.format-date');
    dateElements.forEach(function(element) {
        const date = new Date(element.textContent);
        element.textContent = date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        });
    });

    const timeElements = document.querySelectorAll('.format-time');
    timeElements.forEach(function(element) {
        const time = new Date(`1970-01-01T${element.textContent}`);
        element.textContent = time.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });
    });
});

// دالة لتأكيد الحذف
function confirmDelete(event, message) {
    if (!confirm(message || 'هل أنت متأكد من أنك تريد حذف هذا العنصر؟')) {
        event.preventDefault();
        return false;
    }
    return true;
}

// دالة للتأكد من تحديد خيار واحد فقط من الـ checkboxes
function handleCheckboxSelection(checkbox) {
    // الحصول على معرف العنصر
    const itemId = checkbox.id.split('_')[2];
    const checkboxType = checkbox.id.split('_')[1];

    // إلغاء تحديد الخيارات الأخرى لنفس العنصر
    const otherCheckboxes = document.querySelectorAll(`input[name="status_${itemId}"]`);
    otherCheckboxes.forEach(function(otherCheckbox) {
        if (otherCheckbox.id !== checkbox.id && checkbox.checked) {
            otherCheckbox.checked = false;
        }
    });
}

// دالة لتحديث حقول النموذج بناءً على اختيار آخر
function updateFormFields(selectElement, targetUrl, targetField) {
    const selectedValue = selectElement.value;
    if (!selectedValue) return;

    fetch(`${targetUrl}?id=${selectedValue}`)
        .then(response => response.json())
        .then(data => {
            const targetSelect = document.getElementById(targetField);
            targetSelect.innerHTML = '';

            // إضافة خيار فارغ
            const emptyOption = document.createElement('option');
            emptyOption.value = '';
            emptyOption.textContent = 'اختر...';
            targetSelect.appendChild(emptyOption);

            // إضافة الخيارات من البيانات
            data.forEach(item => {
                const option = document.createElement('option');
                option.value = item.id;
                option.textContent = item.name;
                targetSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error:', error));
}
