let setCategory: any;
(function(){
    document.addEventListener('alpine:init', ()=>{
      Alpine.data('objectSelect', ()=>({
        open:false, 
        listId:'',
        objects: [], // represent filtered results
        original: [],
        isFocused: false, 
        selected: {},
        submitProperty: '', 
        self:undefined,
        newSearch:'', 
        newCategory: {},
        filter(e:Event){
            this.objects = this.original.filter((obj)=> (<string>obj.name).toLowerCase().includes((<HTMLInputElement>e.currentTarget).value.toLowerCase())); 
            if(this.objects.length == 0){
               this.newSearch = (<HTMLInputElement>e.currentTarget).value; 
            }
        }, 
        select(selected:object){
          this.selected = selected; 
          this.open = false; 
          this.objects = [...this.original]
        },
        setup(){
          const items =  [{id: null, name: 'None'}, ...JSON.parse(document.getElementById(this.listId).textContent)]; // added a default selected to be None
          const editProductForm = document.getElementById('edit-product-form');
          this.selected = items[0];
          this.original = items;
          this.objects = items;
          
          if(editProductForm.contains(this.self))
            setCategory = (category:object)=>{
          // TODO: some products don't have categories so I can't actually select one for them. Will find a workaround later.
               if(category){
                  this.selected = category;
               }
               else{
                this.selected = {id: null, name: 'None'};
               }
               this.open = false;
            };
            // I tried returning 'this.setCategory' to a global variable but I was not able to access 'this' object when I called the variable
            // I decided to return 'this' itself and this fixed that issue
          }
      }));
    });
  })()