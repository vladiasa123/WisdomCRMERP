/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { loadBundle } from "@web/core/assets";

export class AcasaHomepage extends Component {}
AcasaHomepage.template = "acasa.Homepage";

registry.category("actions").add("acasa.homepage", AcasaHomepage);
