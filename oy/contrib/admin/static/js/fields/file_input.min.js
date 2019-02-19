/*!
* oy cms frontend assets
* (c) 2019 Musharraf and oy contributers
 */
$(document).on("change",":file",function(){var e=$(this),t=e.get(0).files?e.get(0).files.length:1,i=e.val().replace(/\\/g,"/").replace(/.*\//,"");e.trigger("fileselect",[t,i])}),$(document).ready(function(){$(":file").on("fileselect",function(e,t,i){var n=$(this);$("#"+n.attr("id")+"-info").text("("+t+") "+i)})});