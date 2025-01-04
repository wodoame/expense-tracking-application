type SelectFieldInstance = {
  select: (selected:object)=>void; 
  filter: (e: Event)=>void;
  isOpen: boolean;
};

class SelectFieldManager{
  instances: {[key: string]: SelectFieldInstance}

  getInstance(id:string){
    return this.instances[id]; 
  }

  setInstance(id:string, instance:SelectFieldInstance){
    this.instances[id] = instance; 
  }
}

const selectFieldManager = new SelectFieldManager();

class SelectField{
   instance: SelectFieldInstance; 
   constructor(id: string){
    this.instance = selectFieldManager.getInstance(id);
   }
};

async function fetchJSONData(url: string){
 try{
   const response = await fetch(url);
   const data = await response.json(); 
   return data;   
 }
 catch(e){
  // 
 }
}

let setCategory: any;
(function(){
    document.addEventListener('alpine:init', ()=>{
      Alpine.data('selectField', (id: string)=>({
        isOpen:false, 
        filtered: [], // represent filtered results
        items: [],
        isFocused: false, 
        selected: {},
        submitProperty: '', 
        newSearch:'', 
        newCategory: undefined,
        async init(){
          // original = items
          // objects = filtered
          // open = isOpen
          selectFieldManager.setInstance(id, this);
          this.items = [{id: null, name: 'None'}, ... await fetchJSONData('/categories/')];
          this.selected = this.items[0];
        },
        open(){
          this.isOpen=true;
          this.isFocused=true;
        }, 
        close(){
          this.isOpen=false;
          this.selected = {...this.selected};
          this.filtered = [...this.items];
          this.isFocused = false;
        }, 
        filter(e:Event){
            this.filtered = this.items.filter((obj)=> (<string>obj.name).toLowerCase().includes((<HTMLInputElement>e.currentTarget).value.toLowerCase())); 
            if(this.filtered.length == 0){
               this.newSearch = (<HTMLInputElement>e.currentTarget).value; 
            }
        }, 
        select(selected:object){
          this.selected = selected; 
          this.isOpen = false; 
          this.filtered = [...this.items]
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
  })()