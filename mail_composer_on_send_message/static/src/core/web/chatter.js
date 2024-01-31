/** @odoo-module **/

import { Chatter } from "@mail/core/web/chatter";
import { patch } from "@web/core/utils/patch";


patch(Chatter.prototype, {
    /*
    * Overwrite to pass to the composer model that its component should be opened in a full view
    */
    toggleComposer(mode = false) {
        super.toggleComposer(...arguments);
        if (mode == "message" && this.state.thread && this.state.thread.composer) {
            this.state.thread.composer.onlclick_full = true;
        };
    },
});
