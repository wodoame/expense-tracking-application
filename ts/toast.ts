import Alpine from "alpinejs";

(function(){
  let autoDismiss: boolean;
  document.addEventListener('alpine:init', ()=>{
    Alpine.data('toast', ()=>({
      open:true, 
      autoDismiss:autoDismiss,
      show(){
        if(this.autoDismiss){
          setTimeout(()=>{this.open = false;}, 2000);
        }
      }
    }));
  });
})()