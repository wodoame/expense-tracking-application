import { BaseElement } from "./baseElement";
import { html } from "lit";
import { customElement, property } from "lit/decorators.js";
import { datePickerManager } from "../../../../ts/selectField";


@customElement('expense-date-picker')
export class ExpenseDatePicker extends BaseElement {
    @property({type: String}) accessor currentDate: string;
    onSelectDate(date: string){
        const inputId = this.getAttribute('for');
        if(inputId){
            const input = document.getElementById(inputId) as HTMLInputElement;
            const hiddenInput = document.getElementById(inputId + '-hidden') as HTMLInputElement;
            input.value = new Date(date).toDateString();
            hiddenInput.value = date;
        }
    }

    firstUpdated(): void {
       datePickerManager.setInstance(this.id, this); 
       this.setToday();
    }

    setToday(){
       const inputId = this.getAttribute('for');
         // Get today's date
       const today = new Date();
       // Convert to dateString format
       const dateString = today.toDateString();
       const input = document.getElementById(inputId) as HTMLInputElement;
       const hiddenInput = document.getElementById(inputId + '-hidden') as HTMLInputElement;
       input.value = dateString;
       hiddenInput.value = today.toISOString().split('T')[0];
       this.currentDate = hiddenInput.value; 
    }

    setDate(date:string){
       const inputId = this.getAttribute('for');
       const input = document.getElementById(inputId) as HTMLInputElement;
       const hiddenInput = document.getElementById(inputId + '-hidden') as HTMLInputElement;
       input.value = new Date(date).toDateString();
       hiddenInput.value = date.split('T')[0];
       this.currentDate = hiddenInput.value;
    }
    render() {
        return html`<date-picker .currentDate=${this.currentDate} .onSelectDate=${(date: string) => this.onSelectDate(date)}></date-picker>`;
    }
}