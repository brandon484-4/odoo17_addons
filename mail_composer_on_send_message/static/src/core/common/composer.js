/** @odoo-module **/

import { Composer } from "@mail/core/common/composer";
import { patch } from "@web/core/utils/patch";
import { onMounted } from "@odoo/owl";


patch(Composer.prototype, {
    /*
    * Overwrite to open the message composer in a full view when that's needed
    */
    setup() {
        super.setup(...arguments);
        onMounted(async () => {
            if (this.props.composer.onlclick_full) {
                this.props.composer.onlclick_full = false;
                await this.onClickFullComposer()
            };
        });
    },

});
