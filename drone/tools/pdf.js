const { chromium } = require('playwright'); const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+path.join(__dirname,'parts_list.html'));
await p.pdf({path:path.join(__dirname,'KAT-5_parts_list.pdf'),format:'Letter',printBackground:true,margin:{top:'0.45in',bottom:'0.5in',left:'0.45in',right:'0.45in'},
 displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="font-size:7pt;width:100%;text-align:center;font-family:sans-serif">KAT-5 parts list · page <span class="pageNumber"></span> of <span class="totalPages"></span></div>'});
await p.setViewportSize({width:816,height:1056}); await p.screenshot({path:path.join(__dirname,'page1.png'),fullPage:false});
await b.close();console.log('ok');})();
