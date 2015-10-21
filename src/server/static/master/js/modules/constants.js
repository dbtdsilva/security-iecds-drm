/**=========================================================
 * Module: constants.js
 * Define constants to inject across the application
 =========================================================*/
App
  .constant('APP_COLORS', {
    'primary':                '#5d9cec',
    'success':                '#27c24c',
    'info':                   '#23b7e5',
    'warning':                '#ff902b',
    'danger':                 '#f05050',
    'inverse':                '#131e26',
    'green':                  '#37bc9b',
    'pink':                   '#f532e5',
    'purple':                 '#7266ba',
    'dark':                   '#3a3f51',
    'yellow':                 '#fad732',
    'gray-darker':            '#232735',
    'gray-dark':              '#3a3f51',
    'gray':                   '#dde6e9',
    'gray-light':             '#e4eaec',
    'gray-lighter':           '#edf1f2'
  })
  .constant('APP_MEDIAQUERY', {
    'desktopLG':             1200,
    'desktop':                992,
    'tablet':                 768,
    'mobile':                 480
  })
  .constant('APP_REQUIRES', {
    // jQuery based and standalone scripts
    scripts: {
      'whirl':              ['vendor/whirl/dist/whirl.css'],
      'modernizr':          ['vendor/modernizr/modernizr.js'],
      'icons':              ['vendor/fontawesome/css/font-awesome.min.css',
                             'vendor/simple-line-icons/css/simple-line-icons.css',
                             'vendor/famfamfam-flags/dist/sprite/famfamfam-flags.min.css'],
      'parsley':            ['vendor/parsleyjs/dist/parsley.min.js'],
      'slimscroll':         ['vendor/slimScroll/jquery.slimscroll.min.js'],
      'loadGoogleMapsJS':   ['app/vendor/gmap/load-google-maps.js'],
      'google-map':         ['vendor/jQuery-gMap/jquery.gmap.min.js'],
      'paho-mqtt':          ['vendor/paho-mqtt-js/mqttws31.js'],
      'chart':              ['vendor/Chart.js/Chart.min.js'],
      'timestring':         ['vendor/timestring/dist/timestring.min.js'],
      'lodash':             ['vendor/lodash/lodash.min.js'],
      'highcharts-export':  ['vendor/highstock-release/modules/exporting.js']
    },
    // Angular based script (use the right module name)
    modules: [
      { name: 'toaster',          files: ['vendor/toaster/toaster.min.js',
                                          'vendor/toaster/toaster.min.css']},
      { name: 'ui.gravatar',      files: ['vendor/angular-gravatar/build/md5.js',
                                          'vendor/angular-gravatar/build/angular-gravatar.js'] },
      { name: 'hljs',             files: ['vendor/highlightjs/styles/github.css',
                                          'vendor/highlightjs/highlight.pack.js',
                                          'vendor/angular-highlightjs/angular-highlightjs.js'] },
      { name: 'ngTable',          files: ['vendor/ng-table/dist/ng-table.min.js',
                                          'vendor/ng-table/dist/ng-table.min.css'] },
      { name: 'ngDialog',         files: ['vendor/ngDialog/js/ngDialog.min.js',
                                          'vendor/ngDialog/css/ngDialog.min.css',
                                          'vendor/ngDialog/css/ngDialog-theme-default.min.css'] },
      { name: 'angular-carousel',        files: ['vendor/angular-touch/angular-touch.js',
                                                 'vendor/angular-carousel/dist/angular-carousel.css',
                                                 'vendor/angular-carousel/dist/angular-carousel.js']},
      { name: 'localytics.directives',   files: ['vendor/chosen_v1.3.0/chosen.jquery.min.js',
                                                 'vendor/chosen_v1.3.0/chosen.min.css',
                                                 'vendor/angular-chosen-localytics/chosen.js'] },
      { name: 'angular-underscore',      files: ['vendor/angular-underscore/angular-underscore.min.js'] },
      { name: 'angularMoment',           files: ['vendor/angular-moment/angular-moment.js'] },
      { name: 'uiGmapgoogle-maps',       files: ['vendor/lodash/lodash.min.js',
                                                 'vendor/angular-google-maps/dist/angular-google-maps.min.js'] },
      { name: 'highcharts-ng',           files: ['vendor/highstock-release/highstock.js',
                                                 'vendor/highcharts-ng/dist/highcharts-ng.min.js']},
      { name: 'chart.js',                files: [
        //'vendor/Chart.js/Chart.min.js',
                                                 'vendor/angular-chart.js/dist/angular-chart.min.js',
                                                 'vendor/angular-chart.js/dist/angular-chart.css']}
    ]

  }).constant('angularMomentConfig', {
    preprocess: 'unix', // optional
    //preprocess: 'utc', // optional
    timezone: 'Europe/London' // optional
  })
;
