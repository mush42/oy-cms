$(document).ready(function() {

  var top_level = (window.frameElement && window.dialogArguments) || opener || parent || top;
  if (top_level) {
	$("#side-navigation").hide();
	$("#side-menu-toggler").hide();
  }

});