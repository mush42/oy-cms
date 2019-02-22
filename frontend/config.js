var path = require("path").posix;
var fs = require("fs");


class ContribModule {
	constructor(name) {
		this.name = name;
		this.staticDir = path.normalize(path.join("../oy/contrib", name, "static/"));
	}
}


const modules = [
  new ContribModule("admin"),
  new ContribModule("bootstrap4"),
  new ContribModule("flask_security_templates"),
  new ContribModule("media"),
];

exports.vendorMap = {
  "bootstrap4/bootstrap": [
	"node_modules/bootstrap4/dist/**/*",
    "!**/bootstrap-grid.*",
    "!**/bootstrap-reboot.*",
    "!**/*.map"
  ],
  "bootstrap4/jquery": [
    "node_modules/jquery/dist/jquery.js",
    "node_modules/jquery/dist/jquery.min.js"
  ],
  "bootstrap4/swatch": [
    "node_modules/bootswatch/dist/**",
    "!**/*.scss"
  ],
  "media/magnific-popup": ["node_modules/magnific-popup/dist/**"],
  "admin/bootstrap": [
	"node_modules/bootstrap/dist/**/*",
    "!**/npm.js", 
    "!**/bootstrap-theme.*",
    "!**/*.map"
  ],
  "admin/admin-lte": [
    "node_modules/admin-lte/dist/css/alt/AdminLTE-without-plugin*",
    "node_modules/admin-lte/dist/css/skins/skin-black.*",
    "node_modules/admin-lte/dist/js/*.js",
    "!node_modules/admin-lte/dist/js/demo.js"
  ],
  "admin/font-awesome/css": [
    "node_modules/font-awesome/css/*.css"
  ],
  "admin/font-awesome/fonts": [
    "node_modules/font-awesome/fonts/**"
  ],
  "admin/jquery": [
    "node_modules/jquery/dist/jquery.js",
    "node_modules/jquery/dist/jquery.min.js"
  ],
  "admin/metisMenu": [
    "node_modules/metismenu/dist/*.css",
    "node_modules/metismenu/dist/*.js"
  ],
  "admin/lity": ["node_modules/lity/dist/**"],
  "admin/fields/tagsinput": ["node_modules/jquery.tagsinput-revisited/dist/**"],
  "admin/fields/ckeditor": [
    "node_modules/@ckeditor/ckeditor5-build-classic/build/**",
    "!**/*.map",
  ],
  "admin/toastr": ["node_modules/toastr/build/*.min*"]
}

const oyDeps = {};

for (mod of modules) {
  for (rep of ["dist/css", "dist/js", "vendor"]) {
    let modSpecific = path.join(rep, mod.name);
	if (fs.existsSync(modSpecific)) {
		oyDeps[modSpecific + "/**"] = path.join(mod.staticDir, path.basename(rep));
	} 
  }
}

exports.oyDeps = oyDeps;
exports.contribModules = modules;
