btn_update_selected_text_callback_js = """
function update_selected_text(x) {
    var selected_text_buffer = document.getElementById("selected-text-buffer");
    var selected_text = selected_text_buffer.value;
    console.log(selected_text);
    return selected_text;
}
"""