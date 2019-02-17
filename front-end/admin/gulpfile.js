const autoprefixer = require("autoprefixer");
const cssnano = require("cssnano");
const gulp = require("gulp");
const del = require("del");
const browsersync = require("browser-sync").create();
const header = require("gulp-header");
const cleanCSS = require("gulp-clean-css");
const postcss = require("gulp-postcss");
const rename = require("gulp-rename");
const sass = require("gulp-sass");
const uglify = require("gulp-uglify");
const config = require("./config");

const oy = config.oyAdminStatic;

const banner = ["/*!\n",
  "* oy cms frontend assets\n",
  "* (c) 2019 Musharraf and oy contributers\n",
  " */\n"
].join("");

function browserSync(done) {
  browsersync.init({
    proxy: "localhost:5000"
  });
  done();
}

function browserSyncReload(done) {
  browsersync.reload();
  done();
}

function clean() {
  del([
    "dist/*",
    "vendor/*",
  ]);
  return del(oy + "/*", {force: true});
}

function css() {
  return gulp.src("scss/*.scss")
    .pipe(sass())
    .pipe(header(banner))
    .pipe(gulp.dest("dist/css"))
    .pipe(rename({ suffix: ".min" }))
    .pipe(postcss([autoprefixer(), cssnano()]))
    .pipe(cleanCSS({ compatibility: "ie8" }))
    .pipe(gulp.dest("dist/css"))
    .pipe(browsersync.stream());
}

function js() {
  return gulp.src(["js/**/*.js"])
    .pipe(uglify())
    .pipe(header(banner))
    .pipe(gulp.dest("dist/js"))
    .pipe(rename({ suffix: ".min" }))
    .pipe(gulp.dest("dist/js"))
    .pipe(browsersync.stream());
}

function vendor(done) {
  Object.entries(config.vendorMap).forEach((entry) => {
      gulp.src(entry[1])
      .pipe(gulp.dest("vendor/" + entry[0]))
  })
  done();
}

function copyToOy(done) {
  const fileMap = {
    "vendor/**": oy + "/vendor",
    "dist/css/**": oy + "/css",
    "dist/js/**": oy + "/js"
  }
  Object.entries(fileMap).forEach((entry) => {
      gulp.src(entry[0])
      .pipe(gulp.dest(entry[1]))
  });
  done();
}

function watchFiles() {
  gulp.watch("scss/", css);
  gulp.watch("js", gulp.series(js));
}


const build = gulp.series(clean, gulp.parallel(css, js, vendor));
const copy = gulp.series(build, copyToOy);
const watch = gulp.parallel(watchFiles, browserSync);

// export all tasks
exports.css = css;
exports.js = js;
exports.vendor = vendor;
exports.clean = clean;
exports.watch = watch;
exports.copy = copy;
exports.default = build;
