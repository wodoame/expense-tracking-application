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
