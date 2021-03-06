<!doctype html>
<!--[if lt IE 7]>      <html class="no-js lt-ie9 lt-ie8 lt-ie7" lang=""> <![endif]-->
<!--[if IE 7]>         <html class="no-js lt-ie9 lt-ie8" lang=""> <![endif]-->
<!--[if IE 8]>         <html class="no-js lt-ie9" lang=""> <![endif]-->
<!--[if gt IE 8]><!--> <html class="no-js" lang="" ng-app="myapp"> <!--<![endif]-->
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <title>${title} | Flip/Farm</title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <link rel="shortcut icon" href="/static/images/favicon.ico" type="image/x-icon" />
        <link rel="apple-touch-icon" href="/static/images/apple-touch-icon.png" />
    <link rel="apple-touch-icon" sizes="57x57" href="/static/images/apple-touch-icon-57x57.png" />
    <link rel="apple-touch-icon" sizes="72x72" href="/static/images/apple-touch-icon-72x72.png" />
    <link rel="apple-touch-icon" sizes="76x76" href="/static/images/apple-touch-icon-76x76.png" />
    <link rel="apple-touch-icon" sizes="114x114" href="/static/images/apple-touch-icon-114x114.png" />
    <link rel="apple-touch-icon" sizes="120x120" href="/static/images/apple-touch-icon-120x120.png" />
    <link rel="apple-touch-icon" sizes="144x144" href="/static/images/apple-touch-icon-144x144.png" />
    <link rel="apple-touch-icon" sizes="152x152" href="/static/images/apple-touch-icon-152x152.png" />
    <link rel="apple-touch-icon" sizes="180x180" href="/static/images/apple-touch-icon-180x180.png" />

        <link rel="apple-touch-icon" href="/static/apple-touch-icon.png">

        <link rel="stylesheet" href="/static/css/bootstrap.min.css">
        <style>
            body {
                padding-top: 50px;
                padding-bottom: 20px;
                background-color: #F4F4F4;
            }
			[ng\:cloak], [ng-cloak], [data-ng-cloak], [x-ng-cloak], .ng-cloak, .x-ng-cloak {
  				display: none !important;
			}
        </style>
        <link rel="stylesheet" href="/static/css/bootstrap-theme.min.css">
        <link rel="stylesheet" href="/static/css/font-awesome.min.css">
        <link rel="stylesheet" href="/static/css/awesome-bootstrap-checkbox.css">
        <link rel="stylesheet" href="/static/css/flatty.css">
        <link rel="stylesheet" href="/static/css/vex.css" />
        <link rel="stylesheet" href="/static/css/json.human.css" />
        <link rel="stylesheet" href="/static/css/vex-theme-default.css" />
        <link rel="stylesheet" href="/static/css/main.css">


        <script src="/static/js/vendor/modernizr-2.8.3-respond-1.4.2.min.js"></script>
    </head>
    <body>
        <!--[if lt IE 8]>
            <p class="browserupgrade">You are using an <strong>outdated</strong> browser. Please <a href="http://browsehappy.com/">upgrade your browser</a> to improve your experience.</p>
        <![endif]-->
    <nav class="navbar navbar-inverse navbar-fixed-top" role="navigation">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="/"><em class="fa fa-skyatlas"></em> <b class="text-danger">Flip/Farm</b> <small>RenderFarm Management for Humans</small> <small class="text-danger">${version}</small>
          </a>

        </div>
          <a href="http://pooyamehr.com" target="_new" class="pull-right"><img height="48" class="img" src="/static/images/pooyamehr.png" /></a>

    </nav>



    <div class="container">
        ${body}
      <hr>

      <footer>
			<address>
				 <strong>Pooyamehr Studio</strong> | Farsheed Ashouri<br /> &copy; 2015
            </address>

      </footer>
    </div> <!-- /container -->
        <!-- <script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js"></script> -->
        <script>window.jQuery || document.write('<script src="/static/js/vendor/jquery-1.11.2.min.js"><\/script>')</script>

        <script src="/static/js/vendor/bootstrap.min.js"></script>
        <script src="/static/js/vendor/angular.min.js"></script>
        <script src="/static/js/vendor/angular-cookies.min.js"></script>
        <script src="/static/js/vendor/angular-route.min.js"></script>
        <script src="/static/js/vendor/angular-sanitize.min.js"></script>
        <script src="/static/js/vendor/underscore-min.js"></script>
        <script src="/static/js/vendor/moment.min.js"></script>
        <script src="/static/js/vendor/humane.min.js"></script>
        <script src="/static/js/vendor/vex.combined.min.js"></script>
        <script src="/static/js/vendor/json.human.js"></script>
        <script src="/static/js/plugins.js"></script>
        <script src="/static/js/main.js"></script>

        <!-- Google Analytics: change UA-XXXXX-X to be your site's ID. -->
        <!--
        <script>
            (function(b,o,i,l,e,r){b.GoogleAnalyticsObject=l;b[l]||(b[l]=
            function(){(b[l].q=b[l].q||[]).push(arguments)});b[l].l=+new Date;
            e=o.createElement(i);r=o.getElementsByTagName(i)[0];
            e.src='//www.google-analytics.com/analytics.js';
            r.parentNode.insertBefore(e,r)}(window,document,'script','ga'));
            ga('create','UA-XXXXX-X','auto');ga('send','pageview');
        </script>
        -->
        <script>vex.defaultOptions.className = 'vex-theme-default';</script>
    </body>
</html>
