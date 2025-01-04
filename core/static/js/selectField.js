"use strict";
class SelectFieldManager {
    getInstance(id) {
        return this.instances[id];
    }
    setInstance(id, instance) {
        this.instances[id] = instance;
    }
}
const selectFieldManager = new SelectFieldManager();
class SelectField {
    constructor(id) {
        this.instance = selectFieldManager.getInstance(id);
    }
}
;
async function fetchJSONData(url) {
    try {
        const response = await fetch(url);
        const data = await response.json();
        return data;
    }
    catch (e) {
        // 
    }
}
let setCategory;
(function () {
    document.addEventListener('alpine:init', () => {
        Alpine.data('selectField', (id) => ({
            isOpen: false,
            filtered: [], // represent filtered results
            items: [],
            isFocused: false,
            selected: {},
            submitProperty: '',
            newSearch: '',
            newCategory: undefined,
            async init() {
                // original = items
                // objects = filtered
                // open = isOpen
                selectFieldManager.setInstance(id, this);
                this.items = [{ id: null, name: 'None' }, ...await fetchJSONData('/categories/')];
                this.selected = this.items[0];
            },
            open() {
                this.isOpen = true;
                this.isFocused = true;
            },
            close() {
                this.isOpen = false;
                this.selected = { ...this.selected };
                this.filtered = [...this.items];
                this.isFocused = false;
            },
            filter(e) {
                this.filtered = this.items.filter((obj) => obj.name.toLowerCase().includes(e.currentTarget.value.toLowerCase()));
                if (this.filtered.length == 0) {
                    this.newSearch = e.currentTarget.value;
                }
            },
            select(selected) {
                this.selected = selected;
                this.isOpen = false;
                this.filtered = [...this.items];
            },
            // setup(){
            //   const items =  [, ...JSON.parse(document.getElementById(this.listId).textContent)]; // added a default selected to be None
            //   const editProductForm = document.getElementById('edit-product-form');
            //   this.selected = items[0];
            //   this.original = items;
            //   this.objects = items;
            //   if(editProductForm.contains(this.self))
            //     setCategory = (category:object)=>{
            //        if(category){
            //           this.selected = category;
            //        }
            //        else{
            //         this.selected = {id: null, name: 'None'};
            //        }
            //        this.open = false;
            //     };
            //   }
        }));
    });
})();
