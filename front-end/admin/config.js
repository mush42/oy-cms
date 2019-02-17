
exports.oyAdminStatic = "../../oy/contrib/admin/static/";

exports.vendorMap = {
  "bootstrap": [
	"node_modules/bootstrap/dist/**/*",
    "!**/npm.js", 
    "!**/bootstrap-theme.*",
    "!**/*.map"
  ],
  "bootstrap-daterangepicker": [
    "node_modules/bootstrap-daterangepicker/daterangepicker.*",
    "node_modules/bootstrap-daterangepicker/moment.*",
    "!node_modules/bootstrap-daterangepicker/.*scss"
  ],
  "bootstrap-datepicker": ["node_modules/bootstrap-datepicker/dist/**"],
  "admin-lte": [
    "node_modules/admin-lte/dist/css/*.css",
    "node_modules/admin-lte/dist/css/skins/skin-black.*",
    "node_modules/admin-lte/dist/js/*.js",
    "!node_modules/admin-lte/dist/js/demo.js"
  ],
  "font-awesome/css": [
    "node_modules/font-awesome/css/*.css"
  ],
  "font-awesome/fonts": [
    "node_modules/font-awesome/fonts/**"
  ],
  "jquery": [
    "node_modules/jquery/dist/jquery.js",
    "node_modules/jquery/dist/jquery.min.js"
  ],
  "metisMenu": [
    "node_modules/metismenu/dist/*.css",
    "node_modules/metismenu/dist/*.js"
  ],
  "lity": ["node_modules/lity/dist/**"],
  "fields/tagsinput": ["node_modules/jquery.tagsinput-revisited/dist/**"],
  "fields/ckeditor": [
    "node_modules/@ckeditor/ckeditor5-build-classic/build/**",
    "!**/*.map",
  ],
  "select2": ["node_modules/select2/dist/**"]
}
