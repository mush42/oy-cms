/*!
* oy cms frontend assets
* (c) 2019 Musharraf and oy contributers
 */
$(function(){var a=JSON.parse(document.getElementById("page-metadata").innerHTML),o=document.getElementById("page_type"),i=document.getElementById("page-type-select-form");$(".add-child-btn").click(function(t){$(o).html("");var e=$(this).data("parent-pk"),n=$(this).data("type");$("#parent_pk").val(e),a[n].forEach(function(t){opt=document.createElement("option"),opt.value=t.endpoint,opt.textContent=t.title,o.appendChild(opt)}),swal({title:window.PTYPE_MSG_TXT,content:i,buttons:[{text:window.PTYPE_CANCEL_TXT,value:!1,visible:!0,className:"btn btn-default",closeModal:!0},{text:window.PTYPE_CREATE_TXT,visible:!0,value:!0,className:"btn btn-success",confirm:!0}]}).then(function(t){!0===t&&i.submit()})})});