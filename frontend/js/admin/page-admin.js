$(function() {
  var ptype_meta = JSON.parse(document.getElementById("page-metadata").innerHTML);
  var ptype_select = document.getElementById("page_type");
  var ptype_form = document.getElementById("page-type-select-form");

  $(".add-child-btn").click(function(e) {
    $(ptype_select).html("");
    var pk = $(this).data("parent-pk");
    var type = $(this).data("type");
    $("#parent_pk").val(pk);

    var data = ptype_meta[type];
    data.forEach(function(item) {
      opt = document.createElement("option");
      opt.value = item.endpoint;
      opt.textContent = item.title;
      ptype_select.appendChild(opt);
    });

    swal({
      title: window.PTYPE_MSG_TXT,
      content: ptype_form,
      buttons: [
        {
          text: window.PTYPE_CANCEL_TXT,
          value:false,
          visible: true,
          className: "btn btn-default",
          closeModal: true
        },
       {
        text: window.PTYPE_CREATE_TXT,
        visible: true,
        value: true,
        className: "btn btn-success",
        confirm:  true
      }
    ]
  }).then(function(value) {
      if (value === true) {
      ptype_form.submit();
    }
  });
});
});