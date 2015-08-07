function syntaxHighlight(e){return e?("string"!=typeof e&&(e=JSON.stringify(e,void 0,2)),e=e.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"),e.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,function(e){var t="number";return/^"/.test(e)?t=/:$/.test(e)?"key":"string":/true|false/.test(e)?t="boolean":/null/.test(e)&&(t="null"),'<span class="'+t+'">'+e+"</span>"})):void 0}function pad(e,t){for(var n=e+"";n.length<t;)n="0"+n;return n}humane.timeout=5e3,humane.waitForMove=!0,console.log("Pooyamehr Studio");var prettyDate=function(e){var t=e;return t=isNaN(parseInt(e))?moment(e):moment.unix(e),moment.duration(t-moment()).humanize()},isASCII=function(e,t){var n=(t?/^[\x00-\xFF]*$/:/^[\x00-\x7F]*$/).test(e);return n},getReadableFileSizeString=function(e){var t=-1,n=[" کيلوبایت"," مگابایت"," GB"," TB","PB","EB","ZB","YB"];do e/=1024,t++;while(e>1024);return Math.max(e,.1).toFixed(1)+n[t]},ngApp=angular.module("myapp",["ngRoute","ngSanitize"]);ngApp.directive("stringToNumber",function(){return{require:"ngModel",link:function(e,t,n,o){o.$parsers.push(function(e){return""+e}),o.$formatters.push(function(e){return parseFloat(e,10)})}}}),ngApp.controller("mainCtrl",function(e){e.message="bottle.py boilerplate"}),ngApp.controller("clientCtrl",function(e,t,n,o){e.baseInterval=5e3,e.prettyDate=prettyDate,e.syntaxHighlight=syntaxHighlight,e.moment=moment,e.parseInt=parseInt,e.JsonHuman=JsonHuman,e.pad=pad,e._=_,e.round=Math.round,e.getReadableFileSizeString=getReadableFileSizeString,e.isASCII=isASCII,e.server_status="warning",e.options={},e.options.domain="client",e.options.identity=localStorage.getItem("identity"),e.options.email=localStorage.getItem("email"),e.options.cores=localStorage.getItem("cores"),e.options.queue={},e.options.workerStats=[],e.options.disabledRow=function(e){return"Cancelled"===e?{opacity:.5}:void 0},e.getJobs=function(){var n=t.get("/api/getJobsInfo");n.success(function(t){t.length&&(e.options.queue=t)})},e.updateBenchmark=function(n){if(e.options.qmark=localStorage.getItem("qmark"),!e.options.qmark||n){e.options.qmark=null;var o=t.get("/api/benchmark");o.success(function(t){e.options.qmark=t.qmark,localStorage.setItem("qmark",t.qmark)})}},e.updateBenchmark(),e.options.newJob={category:"Alfred"},e.ping=function(){var n=t.post("/api/pingServer",{qmark:parseInt(e.options.qmark),identity:e.options.identity,email:e.options.email,worker:e.options.workerPing,cores:parseInt(e.options.cores)});n.success(function(t){e.clientInfo=t.clientInfo,"PONG"===t.message?e.server_status="success":e.server_status="danger"}),n.error(function(){e.server_status="danger"})},e.ping(),e.getJobs(),n(function(){e.ping(),e.getJobs()},e.baseInterval),e.uploadFilesChanged=function(n){if(!n.files.length)return null;var o=n.files[0],a=new FormData;a.append("upload",o),a.append("category",e.options.newJob.category),t.post("/api/upload",a,{withCredentials:!0,headers:{"Content-Type":void 0},transformRequest:angular.identity}).success(function(t){var n=_.size(t.data.tasks);humane.log('<span class="text-success"><i class="fa fa-check"></i> '+e.options.newJob.category+" job including <b>"+n+" render tasks</b> added to queue.</span>")}).error(function(){humane.log("An error cccured! Please try again.")})},e.showJobDetails=function(e){console.log(e)},e.updateIdentity=function(){localStorage.setItem("identity",e.options.identity)},e.updateEmail=function(){localStorage.setItem("email",e.options.email)},e.updateCores=function(){localStorage.setItem("cores",e.options.cores)},e.cancelJob=function(e){var n=t.post("/api/cancelJob",{id:e});n.success(function(){humane.log("Job Cancelled.")})},e.pauseJob=function(e){var n=t.post("/api/pauseJob",{id:e});n.success(function(){humane.log("Job Paused.")})},e.resumeJob=function(e){var n=t.post("/api/resumeJob",{id:e});n.success(function(){humane.log("Job queued again.")})},e.tryAgainJob=function(e){var n=t.post("/api/tryAgainJob",{id:e});n.success(function(){humane.log("Job will be sent to dispatch server.")})},e.discardNow=function(){vex.dialog.confirm({message:"Are you sure you want to discard renderes?",callback:function(e){if(e){var n=t.post("/api/discardNow");n.success(function(e){humane.log(e.message)})}}})},e.workerPing=function(){var n=t.get("/api/workerPing");n.success(function(t){t.down?e.options.workerPing=!1:e.options.workerPing=!0})},e.workerStats=function(){var n=t.get("/api/workerStats");n.success(function(t){if(!t.down){var n=_.allKeys(t);e.options.workerStats=t[n],$("#workerStatsDiv").html(JsonHuman.format(t[n]))}})},e.getSlaves=function(){var n=t.get("/api/slaves");n.success(function(t){t&&(e.options.slaves=t)})},e.getJobDetailFunc=function(n,o){var a=t.post("/api/jobDetail",{_id:n});a.success(function(t){e.selectedJob=t,o&&$("#myModal").modal("show")})},e.clearInterval=function(e){clearInterval(e)},e.selectJobAndShowDetails=function(t){e.jobDetailIntervalId&&e.clearInterval(e.jobDetailIntervalId.$$intervalId),e.getJobDetailFunc(t,!0)},o(function(){e.workerPing()},e.baseInterval),n(function(){e.getSlaves()},2*e.baseInterval)});