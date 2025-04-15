// ملف JavaScript لإزالة بطاقة إحصائيات التشيك من صفحة perform_check.html

document.addEventListener('DOMContentLoaded', function() {
    // البحث عن بطاقة إحصائيات التشيك وإزالتها
    const statsCards = document.querySelectorAll('.alert-info.stats-card');
    statsCards.forEach(function(card) {
        if (card.querySelector('.alert-heading') && 
            card.querySelector('.alert-heading').textContent.includes('إحصائيات التشيك')) {
            card.remove();
        }
    });

    // البحث عن أي بطاقة تحتوي على عنوان "إحصائيات التشيك"
    const statsHeaders = document.querySelectorAll('h6');
    statsHeaders.forEach(function(header) {
        if (header.textContent.includes('إحصائيات التشيك')) {
            // البحث عن البطاقة الأم وإزالتها
            let parent = header.parentElement;
            while (parent && !parent.classList.contains('card') && !parent.classList.contains('alert')) {
                parent = parent.parentElement;
            }
            if (parent) {
                parent.remove();
            }
        }
    });
});
