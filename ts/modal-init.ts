class ModalManager{
    modals:any; 
    constructor(){
        this.modals = {}; // a store of created modals
    }

    createModal(id: string, modalInstance: ModalInstance){
        this.modals[id] = modalInstance; 
    }

    getModal(id: string){
        return this.modals[id];
    }
}

const modalManager = new ModalManager();

document.addEventListener('alpine:init', ()=>{
    // this is where the actual creation of a modal instance takes place
    Alpine.data('baseModal', (id: string)=>({
        isOpen: false,
        init(){
            modalManager.createModal(id, this);
        },
        // functionalities defined here can be used in the components directly
        toggle(){
            this.isOpen = !this.isOpen; 
            const animatedBackdrop = document.getElementById('animated-backdrop');
            const body = document.body;
            animatedBackdrop.classList.toggle('hidden');
            body.classList.toggle('overflow-hidden')
        }, 
        handleClickOutside(e: Event){
            if(e.target == e.currentTarget){
                this.toggle();
            }
        }
    }))
});