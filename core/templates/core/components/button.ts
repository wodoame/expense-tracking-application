import { BaseElement } from "./baseElement";
import { html, css } from "lit";
import { customElement, property } from "lit/decorators.js";

@customElement('my-button')
export class MyButton extends BaseElement {
    @property({ type: String }) accessor label = 'Click Me';

    render() {
        return html`<button><slot>${this.label}</slot></button>`;
    }
}