import { BaseElement } from "./baseElement";
import { html } from "lit";
import { customElement, property } from "lit/decorators.js";
import { Calendar } from "vanilla-calendar-pro";
@customElement('date-picker')
export class DatePicker extends BaseElement {

   
    firstUpdated(): void {
        const calendar = new Calendar("#calendar", {
            // Your settings
        });
        calendar.init();
    }
    render() {
        return html`<div id="calendar"></div>`;
    }
}