/** @odoo-module **/

function updateBikeWorkshopBranding() {
    const isBikeWorkshop =
        document.querySelector(
            '.o_main_navbar [data-menu-xmlid="bike_workshop.menu_bike_workshop_root"]'
        ) !== null;

    document.body.classList.toggle(
        "bike-workshop-app",
        isBikeWorkshop
    );
}

function initBikeWorkshopBranding() {
    if (!document.body) {
        return;
    }

    const observer = new MutationObserver(() => {
        updateBikeWorkshopBranding();
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
    });

    updateBikeWorkshopBranding();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initBikeWorkshopBranding);
} else {
    initBikeWorkshopBranding();
}