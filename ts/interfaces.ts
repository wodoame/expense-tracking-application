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
    toggle: (e: Event)=>void; 
    isOpen: boolean; 
}
