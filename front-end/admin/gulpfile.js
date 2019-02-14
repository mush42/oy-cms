var gulp = require('gulp');
var del = require('del');
var less = require('gulp-less');
var browserSync = require('browser-sync').create();
var header = require('gulp-header');
var cleanCSS = require('gulp-clean-css');
var rename = require("gulp-rename");
var uglify = require('gulp-uglify');
var pkg = require('./package.json');


// Set the banner content
var banner = ['/*!\n',
  '* oy cms frontend assets\n',
  '* (c) 2019 Musharraf and oy contributers\n',
  ' */\n'
].join('');

// Compile LESS files from /less into /css
gulp.task('less', function() {
    return gulp.src('less/sb-admin-2.less')
        .pipe(less())
        .pipe(header(banner, { pkg: pkg }))
        .pipe(gulp.dest('dist/css'))
        .pipe(browserSync.reload({
            stream: true
        }))
});

// Minify compiled CSS
gulp.task('minify-css', gulp.series('less'), function() {
    return gulp.src('dist/css/sb-admin-2.css')
        .pipe(cleanCSS({ compatibility: 'ie8' }))
        .pipe(rename({ suffix: '.min' }))
        .pipe(gulp.dest('dist/css'))
        .pipe(browserSync.reload({
            stream: true
        }))
});

// Copy JS to dist
gulp.task('js', function() {
    return gulp.src(['js/sb-admin-2.js'])
        .pipe(header(banner, { pkg: pkg }))
        .pipe(gulp.dest('dist/js'))
        .pipe(browserSync.reload({
            stream: true
        }))
})

// Minify JS
gulp.task('minify-js', gulp.series('js'), function() {
    return gulp.src('js/sb-admin-2.js')
        .pipe(uglify())
        .pipe(header(banner, { pkg: pkg }))
        .pipe(rename({ suffix: '.min' }))
        .pipe(gulp.dest('dist/js'))
        .pipe(browserSync.reload({
            stream: true
        }))
});

// Copy vendor libraries from /node_modules into /vendor
gulp.task('copy', async function() {
    gulp.src(['node_modules/bootstrap/dist/**/*', '!**/npm.js', '!**/bootstrap-theme.*', '!**/*.map'])
        .pipe(gulp.dest('vendor/bootstrap'))

    gulp.src(['node_modules/datatables/media/**/*'])
        .pipe(gulp.dest('vendor/datatables'))

    gulp.src(['node_modules/datatables-plugins/integration/bootstrap/3/*'])
        .pipe(gulp.dest('vendor/datatables-plugins'))

    gulp.src(['node_modules/datatables-responsive/css/*', 'node_modules/datatables-responsive/js/*'])
        .pipe(gulp.dest('vendor/datatables-responsive'))

    gulp.src(['node_modules/font-awesome/**/*', '!node_modules/font-awesome/*.json', '!node_modules/font-awesome/.*'])
        .pipe(gulp.dest('vendor/font-awesome'))

    gulp.src(['node_modules/jquery/dist/jquery.js', 'node_modules/jquery/dist/jquery.min.js'])
        .pipe(gulp.dest('vendor/jquery'))

    gulp.src(['node_modules/metismenu/dist/*'])
        .pipe(gulp.dest('vendor/metisMenu'))

    gulp.src(['node_modules/morrisjs/*.js', 'node_modules/morrisjs/*.css', '!node_modules/morrisjs/Gruntfile.js'])
        .pipe(gulp.dest('vendor/morrisjs'))

})

// Run everything
gulp.task('default', gulp.series('minify-css', 'minify-js', 'copy'));

// Configure the browserSync task
gulp.task('browserSync', function() {
    browserSync.init({
        server: {
            baseDir: ''
        },
    })
})

// Dev task with browserSync
gulp.task('dev', gulp.series('browserSync', 'less', 'minify-css', 'js', 'minify-js'), function() {
    gulp.watch('less/*.less', ['less']);
    gulp.watch('dist/css/*.css', ['minify-css']);
    gulp.watch('js/*.js', ['minify-js']);
    // Reloads the browser whenever HTML or JS files change
    gulp.watch('pages/*.html', browserSync.reload);
    gulp.watch('dist/js/*.js', browserSync.reload);
});

// Clean all target folders
gulp.task('clean:all', function () {
  return del([
    'dist/*',
    'vendor/*',
  ]);
});