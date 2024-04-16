(function ($) {
    "use strict";
    $(window).on("load", function () {
        $(".preloader").fadeOut("slow");
    });
    $(".dropdown-menu a.dropdown-toggle").on("click", function (e) {
        if (!$(this).next().hasClass("show")) {
            $(this).parents(".dropdown-menu").first().find(".show").removeClass("show");
        }
        var $subMenu = $(this).next(".dropdown-menu");
        $subMenu.toggleClass("show");
        $(this)
            .parents("li.nav-item.dropdown.show")
            .on("hidden.bs.dropdown", function (e) {
                $(".dropdown-submenu .show").removeClass("show");
            });
        return false;
    });
    $(".search-btn").on("click", function () {
        $(".search-area").toggleClass("open");
    });
    $(document).on("ready", function () {
        $("[data-background]").each(function () {
            $(this).css("background-image", "url(" + $(this).attr("data-background") + ")");
        });
    });
    new WOW().init();
    function doAnimations(elements) {
        var animationEndEvents = "webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend";
        elements.each(function () {
            var $this = $(this);
            var $animationDelay = $this.data("delay");
            var $animationDuration = $this.data("duration");
            var $animationType = "animated " + $this.data("animation");
            $this.css({ "animation-delay": $animationDelay, "-webkit-animation-delay": $animationDelay, "animation-duration": $animationDuration, "-webkit-animation-duration": $animationDuration });
            $this.addClass($animationType).one(animationEndEvents, function () {
                $this.removeClass($animationType);
            });
        });
    }
   $(".counter").countTo();
    $(".counter-box").appear(
        function () {
            $(".counter").countTo();
        },
        { accY: -100 }
    );
    $(".popup-gallery").magnificPopup({ delegate: ".popup-img", type: "image", gallery: { enabled: true } });
    $(".popup-youtube, .popup-vimeo, .popup-gmaps").magnificPopup({ type: "iframe", mainClass: "mfp-fade", removalDelay: 160, preloader: false, fixedContentPos: false });
    $(window).scroll(function () {
        if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100) {
            $("#scroll-top").addClass("active");
        } else {
            $("#scroll-top").removeClass("active");
        }
    });
    $("#scroll-top").on("click", function () {
        $("html, body").animate({ scrollTop: 0 }, 1500);
        return false;
    });
    $(window).scroll(function () {
        if ($(this).scrollTop() > 50) {
            $(".navbar").addClass("fixed-top");
        } else {
            $(".navbar").removeClass("fixed-top");
        }
    });
    if ($("#countdown").length) {
        $("#countdown").countdown("2030/01/30", function (event) {
            $(this).html(
                event.strftime(
                    "" +
                    '<div class="row">' +
                    '<div class="col countdown-item">' +
                    '<h2 class="mb-0">%-D</h2>' +
                    '<h5 class="mb-0">Day%!d</h5>' +
                    "</div>" +
                    '<div class="col countdown-item">' +
                    '<h2 class="mb-0">%H</h2>' +
                    '<h5 class="mb-0">Hours</h5>' +
                    "</div>" +
                    '<div class="col countdown-item">' +
                    '<h2 class="mb-0">%M</h2>' +
                    '<h5 class="mb-0">Minutes</h5>' +
                    "</div>" +
                    '<div class="col countdown-item">' +
                    '<h2 class="mb-0">%S</h2>' +
                    '<h5 class="mb-0">Seconds</h5>' +
                    "</div>" +
                    "</div>"
                )
            );
        });
    }
    if ($(".select").length) {
        $(".select").niceSelect();
    }
    let date = new Date().getFullYear();
    $("#date").html(date);
    $(".profile-file-btn").on("click", function (e) {
        $(this).next(".profile-file-input").click();
    });
    const getMode = localStorage.getItem("theme");
    if (getMode === "dark") {
        $("body").addClass("theme-mode-variables");
        $(".light-btn").css("display", "none");
        $(".dark-btn").css("display", "block");
    }
    $(".theme-mode-control").on("click", function () {
        $("body").toggleClass("theme-mode-variables");
        const checkMode = $("body").hasClass("theme-mode-variables");
        const setMode = checkMode ? "dark" : "light";
        localStorage.setItem("theme", setMode);
        if (checkMode) {
            $(".light-btn").css("display", "none");
            $(".dark-btn").css("display", "block");
        } else {
            $(".light-btn").css("display", "block");
            $(".dark-btn").css("display", "none");
        }
    });
    $(window).on("load", function () {
        logoMode();
    });
    $(".theme-mode-control").on("click", function () {
        logoMode();
    });
    function logoMode() {
        let dtv = document.querySelector(".theme-mode-variables");
        if (dtv) {
            $(".logo-light-mode").css("display", "block");
            $(".logo-dark-mode").css("display", "none");
        } else {
            $(".logo-light-mode").css("display", "none");
            $(".logo-dark-mode").css("display", "block");
        }
    }
})(jQuery);
