/** @odoo-module */
import { renderToElement } from "@web/core/utils/render";
import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";
publicWidget.registry.get_product_category = publicWidget.Widget.extend({
   selector : 'categories_section',
   async willStart() {
       const result = await rpc('/get_product_categories', {});
       if(result){
           this.$target.empty().html(renderToElement('library_management.category_data', {result: result}))
       }
   },
});
