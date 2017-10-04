// Used to colorize the active link in the nav bar.
// Adds class="active" to any link that is active.
$(document).ready(function() {
    $("[href]").each(function() {
        if (this.href == window.location.href) {
            $(this).addClass("active");
        }
    });
});
