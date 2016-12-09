jQuery(document).ready(function($) {
        $(".sidebar [href]").each(function() {
        if (this.href == window.location.href) {
            $(this).addClass("active");
            }
        });
    });