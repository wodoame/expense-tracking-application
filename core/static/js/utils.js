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
class UniversalCloser {
    constructor() {
        this.instances = {};
    }
    closeExcept(id) {
        const instancesList = Object.values(this.instances);
        instancesList.forEach((instance) => {
            if (instance != this.instances[id]) {
                instance.close();
            }
        });
    }
    subscribe(id, instance) {
        this.instances[id] = instance;
    }
}
;
const categoryPublisher = new CategoryPublisher();
const universalCloser = new UniversalCloser();
