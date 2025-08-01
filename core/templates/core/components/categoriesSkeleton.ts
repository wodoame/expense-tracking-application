import { BaseElement } from "./baseElement";
import { html, css } from "lit";
import { customElement, property } from "lit/decorators.js";

@customElement('categories-skeleton')
export class MyButton extends BaseElement {
    @property({ type: String }) accessor label = 'Click Me';
    generateCards(cards:number = 5){
        return Array.from({ length: cards }, (_, i) => html`
           <div class="bg-gray-50 p-4 rounded-md border dark:bg-dark2 space-y-2 dark:border-darkborder">
         <div class="flex items-center justify-between">
             <div class="h-4 w-32 record-skeleton">
             </div>

             <button>
                 <svg xmlns="http://www.w3.org/2000/svg" class="stroke-gray-500 dark:stroke-gray-400 w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg>
             </button>

         </div>

         <div class="flex items-center justify-between">
             <div class="h-4 w-8 record-skeleton">
             </div>

             <div class="h-4 w-16 record-skeleton">
             </div>
         </div>

     </div>
        `);
    }

    render() {
        return html`
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              ${this.generateCards()}
          </div>
        `;
    }
}