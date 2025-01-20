"use strict";
class Router {
    constructor() {
        this.currentRoute = window.location.pathname;
    }
    async init() {
        const response = await fetch('/routes/?all=1');
        const data = await response.json();
        this.routes = data;
    }
    navigate(route) {
        history.pushState({}, '', route);
        this.currentRoute = route;
        htmx.swap('#main-content', this.routes[route], { swapStyle: 'innerHTML', transition: true });
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
        getSidebar().hide();
    }
}
class Routes {
    constructor(router) {
        this.router = router;
    }
    // To navigate to a route it's as easy as doing: routes.routeName()
    dashboard() {
        this.router.navigate('/dashboard/');
        statSummary.currentType = 'weekly'; // set the stat type to weekly for now
    }
    expenditures() {
        this.router.navigate('/all-expenditures/');
    }
    categories() {
        this.router.navigate('/categories/');
    }
}
const router = new Router();
const routes = new Routes(router);
router.init();
