# Introduction
The method by which 'routing' is done here is by injecting some placeholder HTML snippet (which fetches the actual HTML content) into the browser. <br>
This injection of placeholder HTML content and swapping in actual HTML content gives an effect of page navigation.<br>
The reason for this approach is that the UX is better because the user receives immediate feedback when navigating between pages

## Characteristics of this method
1. Parts of the page which do not need to change remain unchanged.
1. The effect of switching between pages is done on the client side via HTMX. 

# Router class
The Router class is responsible for
1. storing the placholder HTML snippets for each page.
1. 'Navigating' to another page with the help of HTMX

The class is in `ts/router.ts`

```ts
    class Router{
    routes: {
        [path: string]: string;
    }; 
    currentRoute: string  = window.location.pathname;  // initially store the path name of the current url
    async init(){
      // .. 
    }
    navigate(route: string){
        // ... 
    }
}
```
The placeholder HTML snippets are stored in the `routes` property

## Obtaining placholder HTML snippets
The placeholder HTML snippets which will be stored in the `routes` property are generated on the server.
The router has to fetch this the first time the page loads. This is achieved by the `init()` method of the router

```ts
const router = new Router();
router.init(); // fetch placeholder HTML snippets
```
After fetching the placeholder HTML snippets, the `routes` property of the router will store something like this
```ts
{
    '/dashboard/': '...', 
    '/all-expenditures/':'...',
    // ...  
}
```

# Routes class
The routes class is really just an abstraction that provides methods which navigate to a particular page. <br>
A method is created for each route. The class is in `ts/router.ts`

```ts
class Routes{
    router: Router
    constructor(router: Router){
        this.router = router;  // class is initialized with a router 
    }
    dashboard(){
        this.router.navigate('/dashboard/');
    }
    expenditures(){
        this.router.navigate('/all-expenditures/');
    }

    // other routes  
}
```
For example if you wish to navigate to the dashboard using a button you can do this
```html
<button onclick="routes.dashboard()">
    <!-- or with Alpine.js -->
<button x-data @click="routes.dashboard()">
```