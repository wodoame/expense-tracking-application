(function(){
    document.addEventListener('alpine:init', ()=>{
      console.log('alpine has been initialized');
      Alpine.data('themeToggler', ()=>({
        info(){
          console.log('this is working');
            // const prefersDarkTheme = window.matchMedia('(prefers-color-scheme: dark)').matches;
            document.documentElement.classList.toggle('dark');            
        }
      }));
    });
  })()