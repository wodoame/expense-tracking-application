import Alpine from "alpinejs";
import { initFlowbite } from 'flowbite'

window['Alpine'] = Alpine;
document.addEventListener("DOMContentLoaded", () => {
    initFlowbite();
    Alpine.start();
});