// function showFormLoader(id:string){
        // append the id of the current modal toggled to the -form-loader to get the specific loader
    //     const form = <HTMLFormElement>document.getElementById(id); 
    //     const loader = document.getElementById(currentId + '-form-loader');
    //     if(form.checkValidity()){
    //       loader.classList.remove('invisible');
          // form.submit();
    //     } 
    //  }
import { router } from "./router";
let queryParams = {}; // additional query parameters that should be sent with the request (getAdditionalParams function)
const setQueryParameter = (key:string, value:any)=>{
    queryParams[key] = value; 
}

interface FetchOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE';
  data?: any;
  headers?: Record<string, string>;
}

async function fetchJSONData(url: string, options: FetchOptions = {}){
      try{
      const { method = 'GET', data, headers = {} } = options;
      
      // Set default headers
      const defaultHeaders: Record<string, string> = {
        'Content-Type': 'application/json',
        ...headers
      };
      
      // Add CSRF token for non-GET requests (Django requirement)
      if (method !== 'GET') {
        const csrfToken = getCsrfToken();
        if (csrfToken) {
          defaultHeaders['X-CSRFToken'] = csrfToken;
        }
      }
      
      // Prepare fetch configuration
      const fetchConfig: RequestInit = {
        method,
        headers: defaultHeaders
      };
      
      // Add body for non-GET requests
      if (method !== 'GET' && data) {
        fetchConfig.body = JSON.stringify(data);
      }
      
      const response = await fetch(url, fetchConfig);
      
      if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const responseData = await response.json(); 
      return responseData;   
      }
      catch(e){
         console.log('Error fetching data ', e);
         throw e; // Re-throw to allow caller to handle the error
      }
}

// Helper function to get CSRF token from Django
function getCsrfToken(): string | null {
  const csrfCookie = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='));
  
  if (csrfCookie) {
    return csrfCookie.split('=')[1];
  }
  
  // Fallback: try to get from meta tag
  const csrfMeta = document.querySelector('meta[name="csrf-token"]') as HTMLMetaElement;
  if (csrfMeta) {
    return csrfMeta.content;
  }
  
  // Fallback: try to get from hidden input
  const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]') as HTMLInputElement;
  if (csrfInput) {
    return csrfInput.value;
  }
  
  return null;
}

type Subscriber = { 
  update: (data: any)=>void; 
};
class CategoryPublisher{
  subscribers: Subscriber[] = [];
  async fetchLatest(){
      const data = await fetchJSONData('/api/categories/')
      this.notifySubscribers(data);
  }
  subscribe(subscriber: Subscriber){
      this.subscribers.push(subscriber);
  }
  
  unsubscribe(subscriber: Subscriber){
      this.subscribers = this.subscribers.filter((item)=>item != subscriber);  
  }

  notifySubscribers(data: any){
      this.subscribers.forEach((subscriber)=>{subscriber.update(data)})
  }
}

const categoryPublisher = new CategoryPublisher();

const getSidebar = (()=>{
    let instance = undefined; 
    return ():DrawerInstance =>{
        if(instance){
            return instance; 
        }
        
        instance = window['FlowbiteInstances']._instances.Drawer['separator-sidebar']; 
        return instance;
    };
 })(); 

 function getDropdown(id:string){
    return window['FlowbiteInstances']._instances.Dropdown[id];
 }

 function getCategoryName(){
     return decodeURIComponent(window.location.pathname.split('/').filter(segment => segment !== '').pop());
 }

 // This function returns the additional parameters that should be sent with the request
 // It is called during HTMX requests to add additional parameters to the request
 function getAdditionalParams(){
    const result = {...queryParams}; // spread the queryParams object to get a copy of it
    queryParams = {}; // reset the queryParams object to an empty object
   
    // if the current route is a category route, we add the category name and oneCategory flag to the result
    const pattern = /^\/categories\/[^\/]+\/$/;
    if(pattern.test(router.currentRoute)){
        const categoryName =  getCategoryName();
        return {
            categoryName:categoryName,
            oneCategory:1,
            ...result
        }
    }
    return result;
 }

 class StatSummary{
    currentType:string = 'weekly'; 
    fetch(type:string){
        // because #statSummary Element will not be present when the request has not been completed we shouldn't attempt to get it from the DOM again
        if(type != this.currentType){
            this.currentType = type;
            document.getElementById('statSummary').outerHTML = router.routes['/statSummarySkeleton/'];
            htmx.ajax('GET', '/components/statSummary/?type='+ type, {
                target: '#statSummarySkeleton',
                swap:'outerHTML'
        })
        }
    }
 }

 const statSummary = new StatSummary();

 type EventHandler = ()=>void; 

 type EventMap = {
    [key:string]:EventHandler[]
 };

 class EventEmitter {
    events:EventMap; 
    constructor() {
        this.events = {};
    }

    // Add an event listener
    addEventListener(event:string, callback:EventHandler) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        this.events[event].push(callback);
    }

    // Remove an event listener
    removeEventListener(event:string, callback:EventHandler) {
        if (this.events[event]) {
            this.events[event] = this.events[event].filter((cb) => cb !== callback);
        }
    }

    // Trigger an event
    emit(event:string) {
        if (this.events[event]) {
            this.events[event].forEach((callback) => callback());
        }
    }
}

export {
    categoryPublisher,
    fetchJSONData,
    getCsrfToken,
    getSidebar,
    setQueryParameter, 
    statSummary, 
    getDropdown,
    EventEmitter
};

// make globally accessible
window['getAdditionalParams'] = getAdditionalParams;
window['statSummary'] = statSummary;
window['getDropdown'] = getDropdown;