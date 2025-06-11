"use strict";
// function showFormLoader(id:string){
// append the id of the current modal toggled to the -form-loader to get the specific loader
//     const form = <HTMLFormElement>document.getElementById(id); 
//     const loader = document.getElementById(currentId + '-form-loader');
//     if(form.checkValidity()){
//       loader.classList.remove('invisible');
// form.submit();
//     } 
//  }
let queryParams = {}; // additional query parameters that should be sent with the request
const setQueryParameter = (key, value) => {
    queryParams[key] = value;
};
async function fetchJSONData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    }
    catch (e) {
        console.log('Error fetching data ', e);
    }
}
class CategoryPublisher {
    constructor() {
        this.subscribers = [];
    }
    async fetchLatest() {
        const data = await fetchJSONData('/api/categories/');
        this.notifySubscribers(data);
    }
    subscribe(subscriber) {
        this.subscribers.push(subscriber);
    }
    unsubscribe(subscriber) {
        this.subscribers = this.subscribers.filter((item) => item != subscriber);
    }
    notifySubscribers(data) {
        this.subscribers.forEach((subscriber) => { subscriber.update(data); });
    }
}
const categoryPublisher = new CategoryPublisher();
const getSidebar = (() => {
    let instance = undefined;
    return () => {
        if (instance) {
            return instance;
        }
        instance = window['FlowbiteInstances']._instances.Drawer['separator-sidebar'];
        return instance;
    };
})();
function getDropdown(id) {
    return window['FlowbiteInstances']._instances.Dropdown[id];
}
function getCategoryName() {
    return decodeURIComponent(window.location.pathname.split('/').filter(segment => segment !== '').pop());
}
// This function returns the additional parameters that should be sent with the request
// It is called during HTMX requests to add additional parameters to the request
function getAdditionalParams() {
    const result = { ...queryParams }; // spread the queryParams object to get a copy of it
    queryParams = {}; // reset the queryParams object to an empty object
    // if the current route is a category route, we add the category name and oneCategory flag to the result
    const pattern = /^\/categories\/[^\/]+\/$/;
    if (pattern.test(router.currentRoute)) {
        const categoryName = getCategoryName();
        return {
            categoryName: categoryName,
            oneCategory: 1,
            ...result
        };
    }
    return result;
}
class StatSummary {
    constructor() {
        this.currentType = 'weekly';
    }
    fetch(type) {
        // because #statSummary Element will not be present when the request has not been completed we shouldn't attempt to get it from the DOM again
        if (type != this.currentType) {
            this.currentType = type;
            document.getElementById('statSummary').outerHTML = router.routes['/statSummarySkeleton/'];
            htmx.ajax('GET', '/components/statSummary/?type=' + type, {
                target: '#statSummarySkeleton',
                swap: 'outerHTML'
            });
        }
    }
}
const statSummary = new StatSummary();
class EventEmitter {
    constructor() {
        this.events = {};
    }
    // Add an event listener
    addEventListener(event, callback) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        this.events[event].push(callback);
    }
    // Remove an event listener
    removeEventListener(event, callback) {
        if (this.events[event]) {
            this.events[event] = this.events[event].filter((cb) => cb !== callback);
        }
    }
    // Trigger an event
    emit(event) {
        if (this.events[event]) {
            this.events[event].forEach((callback) => callback());
        }
    }
}
const globalEventEmitter = new EventEmitter();
globalEventEmitter.addEventListener('popstate', generateGraph);
