interface Category{
    id: number; 
    name:string;
    product_count:number;
    description?:string; 
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

type DrawerInstance = {
    hide:()=>void;
    show:()=>void;
    toggle: ()=>void;
}
