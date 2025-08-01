interface Category{
    id: number; 
    name:string;
    metrics: CategoryMetrics;
    description?:string; 
}
interface CategoryMetrics{
    total_amount_spent: number;
    product_count: number;
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

type DropdownInstance = {
    open: ()=>void; 
    close: ()=>void; 
    isOpen: boolean;
};

type DrawerInstance = {
    hide:()=>void;
    show:()=>void;
    toggle: ()=>void;
}

