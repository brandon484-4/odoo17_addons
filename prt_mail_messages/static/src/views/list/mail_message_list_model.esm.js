/** @odoo-module **/

import {listView} from "@web/views/list/list_view";

function orderByToString(orderBy) {
    return orderBy.map((o) => `${o.name} ${o.asc ? "ASC" : "DESC"}`).join(", ");
}

export class MailMessageUpdateListModel extends listView.Model {}

export class MailMessageUpdateRecordList extends MailMessageUpdateListModel.DynamicRecordList {
    setup() {
        super.setup(...arguments);
        this.last_offset = 0;
    }

    async _loadRecords() {
        let extraContext = {};
        const rec_len = this.records.length;
        if (this.resModel === "mail.message" && rec_len > 0) {
            extraContext = {
                first_id: this.records[0].resId,
                last_id: this.records[rec_len - 1].resId,
                last_offset: this.last_offset,
                list_count: this.count,
            };
        }
        const kwargs = {
            limit: this.limit,
            offset: this.offset,
            order: orderByToString(this.orderBy),
            context: {
                bin_size: true,
                ...this.context,
                ...extraContext,
            },
        };
        if (this.countLimit !== Number.MAX_SAFE_INTEGER) {
            kwargs.count_limit = this.countLimit + 1;
        }
        const {records: rawRecords, length} =
            this.data ||
            (await this.model.orm.webSearchRead(
                this.resModel,
                this.domain,
                this.fieldNames,
                kwargs
            ));

        const records = await Promise.all(
            rawRecords.map(async (data) => {
                const record = this.model.createDataPoint("record", {
                    resModel: this.resModel,
                    resId: data.id,
                    fields: this.fields,
                    activeFields: this.activeFields,
                    rawContext: this.rawContext,
                    onRecordWillSwitchMode: this.onRecordWillSwitchMode,
                });
                await record.load({values: data});
                return record;
            })
        );

        delete this.data;
        if (length === this.countLimit + 1) {
            this.hasLimitedCount = true;
            this.count = length - 1;
        } else {
            this.count = length;
        }
        this.last_offset = this.offset;

        return records;
    }
}

MailMessageUpdateListModel.DynamicRecordList = MailMessageUpdateRecordList;
