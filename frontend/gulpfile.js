const { src, dest, series, parallel, watch } = require("gulp");
const autoprefixer = require("autoprefixer");
const cssnano = require("cssnano");
const del = require("del");
const browsersync = require("browser-sync").create();
const header = require("gulp-header");
const cleanCSS = require("gulp-clean-css");
const postcss = require("gulp-postcss");
const rename = require("gulp-rename");
const sass = require("gulp-sass");
const uglify = require("gulp-uglify");
const config = require("./config");


const banner = ["/*!\n",
  "* oy cms frontend assets\n",
  "* (c) 2019 Musharraf and oy contributers\n",
  " */\n"
].join("");

async function browserSync() {
  await browsersync.init({
    proxy: "localhost:5000/"
  });
}

async function browserSyncReload() {
  await browsersync.reload();
}

function clean() {
  let toDelete = [
    "dist/*",
    "vendor/*",
  ];
  config.contribModules.forEach((mod) => {
	toDelete.push(mod.staticDir + "/*");
  });
  return del(toDelete, {force: true});
}

function css() {
  return src("scss/**/*.scss")
    .pipe(sass())
    .pipe(header(banner))
    .pipe(dest("dist/css"))
    .pipe(rename({ suffix: ".min" }))
    .pipe(postcss([autoprefixer(), cssnano()]))
    .pipe(cleanCSS({ compatibility: "ie8" }))
    .pipe(dest("dist/css"))
    .pipe(browsersync.stream());
}

function js() {
  return src(["js/**/*.js"])
    .pipe(uglify())
    .pipe(header(banner))
    .pipe(dest("dist/js"))
    .pipe(rename({ suffix: ".min" }))
    .pipe(dest("dist/js"))
    .pipe(browsersync.stream());
}

function vendor(done) {
  Object.entries(config.vendorMap).forEach((entry) => {
      src(entry[1])
      .pipe(dest("vendor/" + entry[0]))
  });
  done();
}

function copyToOy(done) {
  Object.entries(config.oyDeps).forEach((entry) => {
      src(entry[0])
      .pipe(dest(entry[1]))
  });
  done();
}

function watchFiles() {
  watch("scss/**/*.scss", series(css, copyToOy, browserSyncReload));
  watch("js/**/*.js", series(js, copyToOy, browserSyncReload));
  watch("../oy/contrib/**/templates/**/*.html", async function watchTemplates() {
	  await browsersync.reload();
  });
}


const build = series(clean, parallel(css, js, vendor));

// export all tasks
exports.clean = clean;
exports.css = css;
exports.js = js;
exports.vendor = vendor;
exports.build = build;
exports.copy = copyToOy;
exports.watch = parallel(series(watchFiles, css, js), browserSync);
exports.default = series(build, copyToOy);
