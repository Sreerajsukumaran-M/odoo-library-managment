/** @odoo-module */
import { renderToElement } from "@web/core/utils/render";
import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.get_product_tab = publicWidget.Widget.extend({
   selector : '.categories_section',
   async willStart() {
       const result = await rpc('/get_product_categories', {});
       console.log("result=",result)
       if(result && result.categories){
           var chunks=[]
           const data=result.categories;
           for(let i=0 ;i<data.length;i+=4){
               chunks.push(data.slice(i,i+4));
           }
           if (chunks.length >0){
               chunks[0].is_active =true;
           }
           this.chunks = chunks;

       }
   },
    start()
        {const id_number=Math.random()
        if (this.chunks)
        {
         this.$target.empty().html(renderToElement('library_management.category_data', {
         result: this.chunks,
             id_number :id_number,
            }))
        }
    },
});
