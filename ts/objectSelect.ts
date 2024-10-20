let objectSelect: any;
(function(){
    let listId: string;
    let objects: any[] = [];
    let selected = {}; 
    let submitProperty: string; 
    let self:HTMLElement;
    document.addEventListener('alpine:init', ()=>{
      Alpine.data('objectSelect', ()=>({
        open:false, 
        listId:listId,
        objects: objects,
        original: objects,
        isFocused: false, 
        selected: selected,
        submitProperty: submitProperty, 
        self:self,
        filter(e:Event){
            this.objects = this.original.filter((obj)=> (<string>obj.name).toLowerCase().includes((<HTMLInputElement>e.currentTarget).value.toLowerCase())); 
        }, 
        setCategory(category: object){
          // TODO: some products don't have categories so I can't actually select one for them. Will find a workaround later.
         if(category){
           this.selected = category;
         }
         this.open = false;
        },
        setup(){
          const items =  JSON.parse(document.getElementById(this.listId).textContent);
          const editProductForm = document.getElementById('edit-product-form');
          this.selected = items[0];
          this.original = items;
          this.objects = items;
          console.log(this);
          
          if(editProductForm.contains(this.self))
            objectSelect = this;
            // I tried returning 'this.setCategory' to a global variable but I was not able to access 'this' object when I called the variable
            // I decided to return 'this' itself and this fixed that issue
          }
      }));
    });
  })()