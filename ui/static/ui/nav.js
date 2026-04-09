(function () {
    var toggle = document.querySelector('.nav-toggle');
    var panel = document.getElementById('nav-panel');
    if (!toggle || !panel) return;

    var links = panel.querySelectorAll('.nav-link');

    function open() {
        toggle.setAttribute('aria-expanded', 'true');
        panel.hidden = false;
        if (links.length) links[0].focus();
    }

    function close(restoreFocus) {
        toggle.setAttribute('aria-expanded', 'false');
        panel.hidden = true;
        if (restoreFocus) toggle.focus();
    }

    function isOpen() {
        return toggle.getAttribute('aria-expanded') === 'true';
    }

    toggle.addEventListener('click', function () {
        isOpen() ? close(true) : open();
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && isOpen()) close(true);
    });

    document.addEventListener('click', function (e) {
        if (isOpen() && !toggle.contains(e.target) && !panel.contains(e.target)) {
            close(false);
        }
    });

    panel.addEventListener('keydown', function (e) {
        var items = Array.from(links);
        var idx = items.indexOf(document.activeElement);
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            items[(idx + 1) % items.length].focus();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            items[(idx - 1 + items.length) % items.length].focus();
        } else if (e.key === 'Tab') {
            if (!e.shiftKey && idx === items.length - 1) {
                e.preventDefault();
                close(true);
            } else if (e.shiftKey && idx === 0) {
                e.preventDefault();
                close(true);
            }
        }
    });
})();
