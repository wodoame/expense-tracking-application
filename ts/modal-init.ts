class ModalManager{
    modals:any; 
    currentlyOpenModal: ModalInstance | null;  // track the currently opened modal
    constructor(){
        this.modals = {}; // a store of created modals
        this.currentlyOpenModal = null;
    }

    createModal(id: string, modalInstance: ModalInstance){
        this.modals[id] = modalInstance; 
    }

    getModal(id: string){
        return this.modals[id];
    }


}

const modalManager = new ModalManager();
function handleAlpineInitialization(){
    createModal();
}

function createModalInstance(id: string){
    return {
        isOpen: false,
        init(){
            modalManager.createModal(id, this);
        },
        // functionalities defined here can be used in the components directly
        open(){
            this.isOpen = true;
            this.toggleSideEffects(!this.isOpen); 
            history.pushState(null, '');
            localStorage.setItem('modalOpen', 'true');
            modalManager.currentlyOpenModal = this;
        }, 
        close(){
            this.isOpen = false;
            this.toggleSideEffects(!this.isOpen);
            // no matter what closes the modal remove these from localStorage
            localStorage.removeItem('modalOpen');
            localStorage.removeItem('forwarded');
        },
        toggleSideEffects(force:boolean){
            const animatedBackdrop = document.getElementById('animated-backdrop');
            const body = document.body;
            animatedBackdrop.classList.toggle('hidden', force); // note when force is true the class is added and if it's false it is removed
            body.classList.toggle('overflow-hidden', !force);
        }, 
        handleClickOutside(e: Event){
            if(e.target == e.currentTarget){
                this.close();
            }
        }
    }
}

function createModal(){
    Alpine.data('baseModal', createModalInstance);
}

function handleCloseModal(){
    if(localStorage.getItem('modalOpen')){
        localStorage.removeItem('modalOpen');
        localStorage.setItem('forwarded','true')
        history.forward();
    }
    else if(localStorage.getItem('forwarded')){
        modalManager.currentlyOpenModal.close();
    }
}

window.addEventListener('popstate', handleCloseModal);
document.addEventListener('alpine:init', handleAlpineInitialization);
window.addEventListener('beforeunload', ()=>{
    document.removeEventListener('alpine:init', handleAlpineInitialization);  
    window.removeEventListener('popstate', handleCloseModal);
})
