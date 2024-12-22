interface Category{
    id: number; 
    name:string;
}
interface Product{
    id:number; 
    name:string;
    price:number; 
    description:string;
    category: Category;
    date: string;
}

type ModalInstance = {
    toggleSideEffects: (force:boolean)=>void;
    open: ()=>void; 
    close: ()=>void; 
    isOpen: boolean; 
}
