class Router{
    routes: {
        [path: string]: string;
    }
    async init(){
        const response = await fetch('/routes/?all=1');
        const data = await response.json();
        console.log(data);
        this.routes = data;
    }
    navigate(route: string){
        history.pushState({}, '', route); 
        htmx.swap('#main-content', this.routes[route], {swapStyle: 'innerHTML', transition:true});
        getSidebar().hide();
    }
    
}

class Routes{
    router: Router
    constructor(router: Router){
        this.router = router; 
    }
    // To navigate to a route it's as easy as doing: routes.routeName()
    dashboard(){
        this.router.navigate('/dashboard/');
    }
    expenditures(){
        this.router.navigate('/all-expenditures/');
    }
}

const router = new Router();
const routes = new Routes(router);
router.init();
