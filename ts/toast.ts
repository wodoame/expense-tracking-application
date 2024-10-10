(function(){
  document.addEventListener('alpine:init', ()=>{
    Alpine.data('toast', ()=>({
      open:true, 
      show(){
        setTimeout(()=>{this.open = false;}, 2000);
      }
    }));
  });
})()