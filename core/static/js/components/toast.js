(function(){
    document.addEventListener('alpine:init', ()=>{
      Alpine.data('toast', ()=>({
        open:true, 
        close(){
            this.open = false;
        }, 
        
        show(){
            this.open = true;
        }
      }));
    });

})()