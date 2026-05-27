/** @odoo-module **/
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";

registry.category("views").add("event_pass_tree", {
        ...listView,
        buttonTemplate: "event_pass.EventPassListView.buttons",
    }
);