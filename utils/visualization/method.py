load_KG_at_start_js = """
function load_KG_at_start() {

    // wait until jquery & echarts are loaded

    // if (typeof $ === 'undefined' || typeof echarts === 'undefined') {
    //     setTimeout(flush_KG, 100);
    // }else{
    //     flush_KG();
    // }

    setTimeout(function() { document.getElementById("btn-flush-kg").click(); }, 100);

    //;
}
"""


btn_flush_KG_js = """
function btn_flush_KG_js(layout, kg_data_str) {
    console.log("layout: " + layout);
    flush_KG(layout, kg_data_str);
    return layout;
}
"""

click_btn_flush_kg = """(x) => {document.getElementById("btn-flush-kg").click(); return x;}"""

click_btn_query_select_text = """
(x) => {
    document.getElementById("btn-query-select-text").click();

    selected_text_buffer = document.getElementById("selected-text-buffer");
    selected_text_buffer.value = x;
    
    return x;
}
"""