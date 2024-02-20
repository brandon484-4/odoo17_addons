/** @odoo-module **/

import {ListRenderer} from "@web/views/list/list_renderer";

export class MailMessageUpdateListRenderer extends ListRenderer {
    getCellTitle(column, record) {
        if (column.name === "subject_display") {
            return false;
        }
        return super.getCellTitle(column, record);
    }
}
