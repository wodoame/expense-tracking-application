import { weeklyChartData } from "../core/templates/core/components/weeksChart";
import { monthlyChartData } from "../core/templates/core/components/monthsChart";
import { weeksRecordsStore } from "../core/templates/core/components/weeksRecords";
import { router } from "./router";

interface HistoryHandlers{
    [path:string]: Handler[]
};

type Handler = ()=>void;

class HistoryHandler{
    handlers:HistoryHandlers = {};
    addHandler(path:string, handler:()=>any){
        if(!this.handlers[path]){
            this.handlers[path] = [handler]
        }
        else{
            this.handlers[path].push(handler)
        }
    }

    handle(path: string,e: PopStateEvent){
        if(this.handlers[path]){
            this.handlers[path].forEach(handler => handler());
        }

        if(e.state && path != '/weeks/'){
            document.getElementById('main-content').innerHTML = e.state.html;
        }
    }
}

export const hh = new HistoryHandler(); 
hh.addHandler('/dashboard/', ()=>{
    weeklyChartData.useCachedData = true; // use cached data when navigating back to dashboard
    monthlyChartData.useCachedData = true; // use cached data when navigating back to dashboard
});

hh.addHandler('/weeks/', ()=>{
      weeksRecordsStore.useCachedData = true; // set the flag to true so that the component can use cached data
      document.getElementById('main-content').innerHTML = router.routes['/weeks/'];
      document.getElementById('pageHeading').textContent = 'Weeks';
});