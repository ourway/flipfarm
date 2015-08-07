/*global angular*/
/*global console*/
/*global moment*/
/*global humane*/
/*global Math*/
/*global _*/
/*global vex*/
/*global JsonHuman*/

humane.timeout = 5000; // default: 2500
humane.waitForMove = true; // default: false

console.log('Pooyamehr Studio');

function syntaxHighlight(json) {
        if (!json){
                return;
        }
    if (typeof json !== 'string') {
         json = JSON.stringify(json, undefined, 2);
    }
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        var cls = 'number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'key';
            } else {
                cls = 'string';
            }
        } else if (/true|false/.test(match)) {
            cls = 'boolean';
        } else if (/null/.test(match)) {
            cls = 'null';
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}

var prettyDate = function (time) {
  var _d = time;
  if (!isNaN(parseInt(time)))
        {
                _d = moment.unix(time);
        }
  else
        {
                _d = moment(time);
        }
  return moment.duration(_d - moment()).humanize();
};
var isASCII = function (str, extended) {
  var data = (extended ? /^[\x00-\xFF]*$/ : /^[\x00-\x7F]*$/).test(str);
  return data;
};
var getReadableFileSizeString = function (fileSizeInBytes) {
  var i = -1;
  var byteUnits = [
    ' \u06A9\u064A\u0644\u0648\u0628\u0627\u06CC\u062A',
    ' \u0645\u06AF\u0627\u0628\u0627\u06CC\u062A',
    ' GB',
    ' TB',
    'PB',
    'EB',
    'ZB',
    'YB'
  ];
  do {
    fileSizeInBytes = fileSizeInBytes / 1024;
    i++;
  } while (fileSizeInBytes > 1024);
  return Math.max(fileSizeInBytes, 0.1).toFixed(1) + byteUnits[i];
};
function pad(num, size) {
  var s = num + '';
  while (s.length < size)
  {
        s = '0' + s;
  }
  return s;

}






var ngApp = angular.module('myapp', ['ngRoute', 'ngSanitize']);


ngApp.directive('stringToNumber', function() {
  return {
    require: 'ngModel',
    link: function(scope, element, attrs, ngModel) {
      ngModel.$parsers.push(function(value) {
        return '' + value;
      });
      ngModel.$formatters.push(function(value) {
        return parseFloat(value, 10);
      });
    }
  };
});

ngApp.controller('mainCtrl', function($scope) {
	$scope.message = "bottle.py boilerplate";
});


ngApp.controller('clientCtrl', function($scope, $http, $interval, $timeout) {
        $scope.baseInterval = 5000;
        $scope.prettyDate = prettyDate;
        $scope.syntaxHighlight = syntaxHighlight;
        $scope.moment = moment;
        $scope.parseInt = parseInt;
        $scope.JsonHuman = JsonHuman;
        $scope.pad = pad;
        $scope._ = _;
        $scope.round = Math.round;
        $scope.getReadableFileSizeString = getReadableFileSizeString;
        $scope.isASCII = isASCII;
        $scope.server_status = 'warning';
        $scope.options = {};
        $scope.options.domain = 'client';
        $scope.options.identity = localStorage.getItem('identity');
        $scope.options.email = localStorage.getItem('email');
        $scope.options.cores = localStorage.getItem('cores');
        $scope.options.queue = {};
        $scope.options.workerStats=[];
        $scope.options.disabledRow=function(_status){
                if (_status==='Cancelled'){
                        return {'opacity':0.5};
                }

        };

        $scope.getJobs = function(){
                var jr = $http.get('/api/getJobsInfo');
                jr.success(function(queueData){
                        if (queueData.length){
                                $scope.options.queue = queueData;
                        }
                });
        };
        $scope.updateBenchmark = function(reload){
                $scope.options.qmark = localStorage.getItem('qmark');
                if (!$scope.options.qmark || reload){
                $scope.options.qmark = null;
                var br = $http.get('/api/benchmark');
                br.success(function(data){
                        $scope.options.qmark = data.qmark;
                        localStorage.setItem('qmark', data.qmark);
                });
        }
        };

        $scope.updateBenchmark();
        $scope.options.newJob = {'category':'Alfred'};
        $scope.ping = function(){
                var pr = $http.post('/api/pingServer', {qmark:parseInt($scope.options.qmark),
                                                        identity:$scope.options.identity,
                                                        email:$scope.options.email,
                                                        worker:$scope.options.workerPing,
                                                        cores:parseInt($scope.options.cores),
                                                        });
                pr.success(function(result){
                        $scope.clientInfo = result.clientInfo;
                        if (result.message==='PONG'){
                                $scope.server_status = 'success';
                        }
                        else{
                                $scope.server_status = 'danger';

                        }
                });
                pr.error(function(){
                        $scope.server_status = 'danger';
                });
        };
        $scope.ping();
        $scope.getJobs();
        $interval(function(){
                $scope.ping();
                $scope.getJobs();
        }, $scope.baseInterval);
        $scope.uploadFilesChanged = function(e){
                if (!e.files.length){
                        return null;}
                var file = e.files[0];
                var fd = new FormData();
                            fd.append("upload", file);
                            fd.append("category", $scope.options.newJob.category);
                            $http.post('/api/upload', fd, {
                                withCredentials: true,
                                headers: {'Content-Type': undefined },
                                transformRequest: angular.identity
                            }).success(function(result){
                                var framesCount = _.size(result.data.tasks);
                                humane.log('<span class="text-success"><i class="fa fa-check"></i> '+$scope.options.newJob.category + ' job including <b>' + framesCount + ' render tasks</b> added to queue.</span>');
                            }).error(function(){
                                humane.log('An error cccured! Please try again.');
                            });//.success().error();


        };

        $scope.showJobDetails = function(jid){
                console.log(jid);
        };

        $scope.updateIdentity = function(){
                localStorage.setItem('identity', $scope.options.identity);
        };
        $scope.updateEmail = function(){
                localStorage.setItem('email', $scope.options.email);
        };
        $scope.updateCores = function(){
                localStorage.setItem('cores', $scope.options.cores);
        };
        $scope.cancelJob = function(jobId){
                var cr = $http.post('/api/cancelJob', {'id':jobId});
                cr.success(function(){
                        humane.log('Job Cancelled.');
                });
        };

        $scope.pauseJob = function(jobId){
                var cr = $http.post('/api/pauseJob', {'id':jobId});
                cr.success(function(){
                        humane.log('Job Paused.');
                });
        };
        $scope.resumeJob = function(jobId){
                var cr = $http.post('/api/resumeJob', {'id':jobId});
                cr.success(function(){
                        humane.log('Job queued again.');
                });
        };

         $scope.tryAgainJob = function(jobId){
                var cr = $http.post('/api/tryAgainJob', {'id':jobId});
                cr.success(function(){
                        humane.log('Job will be sent to dispatch server.');
                });
        };

        $scope.discardNow = function(){

                vex.dialog.confirm({
                        message: 'Are you sure you want to discard renderes?',
                        callback: function(value) {
                        if (value){
                                var disr = $http.post('/api/discardNow');
                                disr.success(function(result){
                                        humane.log(result.message);
                                });
                                }
                        }
                });

        };


        $scope.workerPing = function(){
                        var wp = $http.get('/api/workerPing');
                        wp.success(function(result){
                                if (!result.down){
                                        $scope.options.workerPing=true;
                                }
                                else{
                                        $scope.options.workerPing=false;

                                }
                });
        };

        $scope.workerStats = function(){
                        var wp = $http.get('/api/workerStats');
                        wp.success(function(result){
                                if (!result.down){
                                        var _k = _.allKeys(result);
                                        $scope.options.workerStats=result[_k];
                                        $('#workerStatsDiv').html(JsonHuman.format(result[_k]));

                                }
                });
        };

        $scope.getSlaves = function(){
                        var sr = $http.get('/api/slaves');
                        sr.success(function(result){
                                if (result){
                                        $scope.options.slaves=result;
                                }
                });
        };

        $scope.selectJobAndShowDetails = function(jobId){
            var jr = $http.post('/api/jobDetail', {'_id':jobId});
            jr.success(function(data){
                $scope.selectedJob = data;
                $('#myModal').modal('show');
            });
        };

        $timeout(function(){
                $scope.workerPing();}, $scope.baseInterval);
        $interval(function(){
                //$scope.workerPing();
                $scope.getSlaves();
        }, $scope.baseInterval*2);



});
