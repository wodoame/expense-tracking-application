import Alpine from "alpinejs";

(function(){
    document.addEventListener('alpine:init', ()=>{
      Alpine.data('themeToggler', ()=>({
        dark:localStorage.getItem('dark') == 'true', 
        toggle(){
            this.dark = !this.dark;
            document.documentElement.classList.toggle('dark', this.dark);   
            localStorage.setItem('dark', this.dark? 'true': 'false')
            document.documentElement.setAttribute('data-theme', this.dark?'dark':'light');
        }
      }));
    });
  })()