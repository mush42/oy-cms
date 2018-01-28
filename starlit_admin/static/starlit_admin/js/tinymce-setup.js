(function(){

function custom_file_browser(field_name, url, type, win){
    tinyMCE.activeEditor.windowManager.open({
        file : window.__file_browser_url + '?popup=1' + '&type=' + type + '&old=' + url,
        title : 'My File Browser',
        width : 800,
        height : 500,
        resizable : "yes",
        close_previous : "no"
    }, {
        window : win,
        input : field_name
    });
    return false;
}

tinyMCE.init({
	selector: "textarea.mceEditor",
    height: '500px',
	theme: 'modern',
	language: window.__language,
    directionality : window.__lang_dir,
	file_browser_callback: custom_file_browser,
    images_upload_url: '/upload',
	plugins: [
		"directionality", "advlist autolink lists link image charmap print preview anchor",
		"searchreplace visualblocks code fullscreen",
		"insertdatetime media table contextmenu paste",
		"emoticons imagetools tabfocus spellchecker textpattern"
	],
    toolbar: [
		"insertfile undo redo | spellchecker | bold italic | " +
		"alignleft aligncenter alignright alignjustify | " +
		"bullist numlist outdent indent | link image emoticons table" +
		"insertdatetime code  fullscreen preview"
    ]
})
})()