// LifeOS - Frontend interactions

(function() {
    'use strict';

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    const csrftoken = getCookie('csrftoken');

    function ajaxPost(url, data) {
        const formData = new FormData();
        if (data) {
            for (const k in data) formData.append(k, data[k]);
        }
        return fetch(url, {
            method: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            body: formData,
            credentials: 'same-origin',
        }).then(r => r.json());
    }

    // ----------- Routine task complete toggle -----------
    document.querySelectorAll('[data-toggle-task]').forEach(el => {
        el.addEventListener('click', function() {
            const taskId = this.dataset.toggleTask;
            const card = this.closest('.timeline-item');
            ajaxPost(`/routines/${taskId}/toggle/`).then(data => {
                if (data.is_completed) {
                    this.classList.add('completed');
                    this.innerHTML = '✓';
                    card.querySelector('.timeline-card').classList.add('completed');
                } else {
                    this.classList.remove('completed');
                    this.innerHTML = '';
                    card.querySelector('.timeline-card').classList.remove('completed');
                }
            });
        });
    });

    // ----------- Mood selection -----------
    document.querySelectorAll('[data-mood]').forEach(el => {
        el.addEventListener('click', function() {
            const mood = this.dataset.mood;
            document.querySelectorAll('[data-mood]').forEach(m => m.classList.remove('selected'));
            this.classList.add('selected');
            ajaxPost('/routines/mood/', { mood: mood });
        });
    });

    // ----------- Energy selection -----------
    document.querySelectorAll('[data-energy]').forEach(el => {
        el.addEventListener('click', function() {
            const energy = this.dataset.energy;
            document.querySelectorAll('[data-energy]').forEach(m => m.classList.remove('active'));
            this.classList.add('active');
            ajaxPost('/routines/mood/', { energy: energy });
        });
    });

    // ----------- Water quick add -----------
    document.querySelectorAll('[data-water-add]').forEach(el => {
        el.addEventListener('click', function(e) {
            e.preventDefault();
            const amt = this.dataset.waterAdd || '0.25';
            ajaxPost('/health/water/add/', { amount: amt }).then(data => {
                // Update every water total on the page (tile + summary card)
                document.querySelectorAll('[data-water-total]').forEach(elm => {
                    elm.textContent = data.total.toFixed(1);
                });
                const percentEl = document.querySelector('[data-water-percent]');
                if (percentEl) percentEl.textContent = data.percent + '%';
                const bar = document.querySelector('[data-water-bar]');
                if (bar) bar.style.width = data.percent + '%';
            });
        });
    });

    // ----------- Dark mode toggle -----------
    const darkToggle = document.getElementById('dark-mode-toggle');
    if (darkToggle) {
        darkToggle.addEventListener('change', function() {
            ajaxPost('/accounts/toggle-dark/').then(data => {
                if (data.dark_mode) document.body.classList.add('dark-mode');
                else document.body.classList.remove('dark-mode');
            });
        });
    }

    // Auto-dismiss toasts
    setTimeout(() => {
        document.querySelectorAll('.toast').forEach(t => {
            t.style.transition = 'opacity 0.5s';
            t.style.opacity = '0';
            setTimeout(() => t.remove(), 500);
        });
    }, 3500);

})();
