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
        htmx.swap('#main-content', this.routes[route], {swapStyle: 'innerHTML', transition:true})
    }
    
}

class Routes{
    router: Router
    constructor(router: Router){
        this.router = router; 
    }
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
