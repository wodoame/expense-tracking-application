class Router{
    routes: {
        [path: string]: string;
    }; 
    currentRoute: string  = window.location.pathname; 
    async init(){
        const response = await fetch('/routes/?all=1');
        const data = await response.json();
        this.routes = data;
    }
    navigate(route: string, forcedRoute?:string){
        history.replaceState({html: document.getElementById('main-content').innerHTML}, '') // store html for the current page
        history.pushState(null, '', forcedRoute?forcedRoute:route); // push url for the next page
        this.currentRoute = forcedRoute?forcedRoute:route;
        htmx.swap('#main-content', this.routes[route], {swapStyle: 'innerHTML', transition:true});
        window.scrollTo({
            top: 0, 
            behavior: 'smooth'
        });
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
        statSummary.currentType = 'weekly'; // set the stat type to weekly for now
    }
    expenditures(){
        this.router.navigate('/all-expenditures/');
    }
    categories(){
         this.router.navigate('/categories/');
    }
    category(categoryName:string){
       this.router.navigate('/categories/category-name/', `/categories/${categoryName}/`);
       document.getElementById('pageHeading').textContent = categoryName;
    }
    viewWeek(id: number, dateRange: string){
        // -1 represents a week that does not exist
        if(id != -1){
            setQueryParameter('week_id', id); // add week_id to the query parameters
            this.router.navigate('viewWeekSkeleton', `/weeks/${id}/`);
            document.getElementById('pageHeading').textContent = `${dateRange}`;
        }
    } 
}

const router = new Router();
const routes = new Routes(router);
router.init();
