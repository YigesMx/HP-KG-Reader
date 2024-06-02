read_selection_js_html_head = '''
<script>
function read_selection_shortcut(e) {
    var event = document.all ? window.event : e;
    switch (e.target.tagName.toLowerCase()) {
        //case "input":
        //case "textarea":
        //break;
        default:
        if (e.key.toLowerCase() == "s" && e.shiftKey) {
            selected_text = window.getSelection().toString();

            //console.log(selected_text);

            //获取 selected-text-buffer 元素
            var selected_text_buffer = document.getElementById("selected-text-buffer");

            //设置 input 元素的 value 为选中的文本
            selected_text_buffer.value = selected_text;

            //按下更新text按钮
            setTimeout(function() {
                document.getElementById("btn-update-selected-text").click();
            }, 0);

            //按下查询按钮
            setTimeout(function() {
                document.getElementById("btn-query-select-text").click();
            }, 50);
        } else if (e.key.toLowerCase() == "a" && e.shiftKey) {
            selected_text = window.getSelection().toString();

            //console.log(selected_text);

            //获取 selected-text-buffer 元素
            var selected_text_buffer = document.getElementById("selected-text-buffer");

            //设置 input 元素的 value 追加 "&&选中的文本"
            selected_text_buffer.value += "&&" + selected_text;

            //按下更新text按钮
            setTimeout(function() {
                document.getElementById("btn-update-selected-text").click();
            }, 0);

            //按下查询按钮
            setTimeout(function() {
                document.getElementById("btn-query-select-text").click();
            }, 50);
        }
    }
}
document.addEventListener('keypress', read_selection_shortcut, false);
</script>
'''