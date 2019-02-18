$(document).ready(function() {

  $(".media-clear-btn").click(function(e) {
      var input_id = $(this).data("input-id");
      $("#" + input_id).val("");
      $("#selected-media-preview-" + input_id).addClass("visually-hidden");
      $("#nothing-selected-" + input_id).removeClass("visually-hidden");
      $("#selected-media-preview-" + input_id).attr("aria-hidden", "true");
      $("#nothing-selected-" + input_id).attr("aria-hidden", "false");
  });

  $(".media-popup-openner").click(function() {
    window.current_popup = lity($(this).data("popup-target"));
    window.current_popup.input_id = $(this).data("input-id");;
  })

  $(document).on('lity:close', function(event, instance) {
    var rv = instance.returned_data;
    var input_id = instance.input_id;
    $("#" + input_id).val(rv.id);
    $("#selected-media-preview-" + input_id).removeClass("visually-hidden");
    $("#nothing-selected-" + input_id).addClass("visually-hidden");
    $("#selected-media-preview-" + input_id).attr("aria-hidden", "false");
    $("#nothing-selected-" + input_id).attr("aria-hidden", "true");
    $("#" + input_id + "_preview").attr("src", rv.src);
    $("#" + input_id + "_preview").attr("alt", rv.title);
  });

});