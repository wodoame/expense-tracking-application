"use strict";
(function () {
    document.addEventListener('alpine:init', () => {
        Alpine.data('toast', () => ({
            open: false,
            // close(){
            //   setTimeout(()=>{this.open = false; localStorage.setItem('toastAppeared', 'true')}, 2000);
            // }, 
            show() {
                this.open = true;
                setTimeout(() => { this.open = false; }, 2000);
            }
        }));
    });
})();
