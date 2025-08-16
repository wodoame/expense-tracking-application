import { BaseElement } from "./baseElement";
import { html } from "lit";
import { customElement, property } from "lit/decorators.js";

@customElement('date-input')
export class DateInput extends BaseElement {
    
    render() {
        return html`
        <div>
            <input type="text" id="" class="input">
        </div>
        <input type="hidden" name="{{name}}" id="{{id}}-value">
        `;
    }
}