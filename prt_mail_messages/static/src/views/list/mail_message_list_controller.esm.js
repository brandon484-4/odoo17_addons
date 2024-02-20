/** @odoo-module **/

import {ListController} from "@web/views/list/list_controller";

export class MailMessageUpdateListController extends ListController {
    setup() {
        super.setup();
        this.editable = false;
    }
}
