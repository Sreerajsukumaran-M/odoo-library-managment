/** @odoo-module **/
import { registry } from "@web/core/registry";
import { download } from "@web/core/network/download";

registry.category("ir.actions.report handlers").add("xlsx", async(action)=> {
  if (action.report_type === 'xlsx') {
      await download({
          url: '/xlsx_reports',
          data: action.data,
          // complete: () => unblockUI,
          error: (error) => console.error("XLSX download error:", error),
           });
           return true
  }
});
