      <!-- Example row of columns -->
<div class="panel panel-{{server_status}}"  ng-controller="clientCtrl"  ng-cloak>
        <div class="panel panel-heading">
                <span ng-show="server_status" class="pull-right">
                                <a href="/server"
                                        class="badge"
                                        ng-show="server_status==='success'"><b> <em class="fa fa-server fa-5x"></em> <i class="fa fa-circle-o-notch fa-spin fa-circle"></i> Connected</b></a>
                                <span ng-show="server_status==='warning'">Connecting Server</span>
                                <span ng-show="server_status==='danger'">Server is <b>DOWN</b></span>
                </span>
                <h3><span><em  class='fa fa-dashboard fa-2x'></em> Client Dashboard</span></h3>
      </div>
      <div class="panel panel-body" id="mainDiv">
                <div class="col-md-12">
                        <div ng-show="server_status==='danger'" class="alert alert-warning"><h4>
                        <em class="fa fa-info-circle"></em>
                        <b>Flip/Farm</b> Server is Down</h4>
                                <p>Please check <code>config.json</code> file and update server address</p>
                        </div>
                </div>

        <div class="col-md-4" ng-if="server_status==='success'">
                <div class="panel panel-default">
                        <div class="panel panel-heading"><h4>
                        <em class="fa fa-cloud-upload"></em>
                        Add a new Job</h4></div>
                        <div class="panel panel-body">
                                 <select class="form-control" name="category" ng-model="options.newJob.category">
                                        <option>Fearless Render Job Format</option>
                                        <option>Alfred</option>
                                        <option>Rib File</option>
                                        <option>Maya Scene File</option>
                                        <option>Nuke Script</option>
                                        <option>Houdini hip</option>
                                </select>
                                <hr/>
                                <button class="btn btn-default btn-lg" ng-class="{'disabled':!options.newJob.category}"
                                        onclick="document.getElementById('selectNewFile').click();">

                                        <em class="fa fa-plus"></em> Add to Queue </button>
                                <input type="file" id="selectNewFile"
                                onchange="angular.element(this).scope().uploadFilesChanged(this)"
                                class="hidden" name="upload"/>

                        </div>
                </div>

                <div class="panel panel-info">
                        <div class="panel panel-heading">
                                <h4 ng-class="{'text-success':clientInfo.qmark}">
                                <em class="fa fa-desktop"></em>
                                Client Information</h4></div>
                        <div class="panel panel-body">
<div style="margin-top:-20px;" title="CPU Usage">
<label>
CPU Usage
</label>
<small class="text-primary" ng-show="options.cores==clientInfo.cpu_count">All cores are available</small>
<small class="text-info" ng-hide="options.cores==clientInfo.cpu_count || options.cores==0">Just <b>{{options.cores}}</b>
        core<span ng-show="options.cores>1">s</span>
        <span ng-show="options.cores>1">are</span>
        <span ng-show="options.cores<2">is</span>
        available</small>
<small class="text-warning" ng-show="options.cores==0">Not a slave for rendering</small>
<div ng-repeat="cpu in clientInfo.cpu.percpu track by $index">
<div class="progress" style="opacity:0.75">
<div class="progress-bar"
        ng-class="{'progress-bar-danger':cpu>50, 'progress-bar-info':cpu<=50 && cpu>25, 'progress-bar-success':cpu<=25}"
        role="progressbar" aria-valuenow="{{cpu}}"
  aria-valuemin="0" aria-valuemax="100" style="width:{{cpu}}%">
<small ng-if="cpu>15" class="pull-right" style="color:#fff;margin-right:10%"><b>{{cpu}}</b>%</small>
  </div>
</div>
</div>
</div>



                        <hr/>
                                <table class="table table-responsive table-stripped table-hover">
                                        <tr>
                                                <td>IP</td>
                                                <td><code>{{clientInfo.ip}}</code></td>
                                        </tr>
                                        <tr>
                                                <td>user</td>
                                                <td><code>{{clientInfo.user}}</code></td>
                                        </tr>
                                        <tr>
                <td
        title="The identity is used to recongize current machine in server. Setting identity is highly recommended.">Identity</td>
                                                <td><code ng-show="clientInfo.identity">{{clientInfo.identity}}</code>
                                                        <div ng-hide="clientInfo.identity"
                                                                class="alert alert-warning">
                                                                        <i class="fa fa-info-circle"></i>
                                                                        Please set your <br/>identity in
                                                                        <span class="text-primary">
                                                                        <i class="fa fa-gear"></i> settings</span> tab.
                                                                </div>

                                                </td>
                                        </tr>
                                        <tr class="active">
                                                <td><b>Speed</b></td>
                                                <td><span class=""><code
                                                ng-show="clientInfo.qmark">{{clientInfo.qmark*clientInfo.cpu_count}}</code>

                                                </span>
                                                </td>
                                        </tr>
                                        <tr>
                                                <td>Cores</td>
                                                <td><code>{{clientInfo.cpu_count}}</code> Cores</td>
                                        </tr>
                                        <tr>
                                                <td>CPU</td>
                                                <td><code>{{clientInfo.cpu.overall}}%</code></td>
                                        </tr>
                                        <tr>
                                                <td>Memory</td>
                                                <td><code>{{100-round(clientInfo.memory.free_memory*100/clientInfo.memory.real_mem_total)}}%</code> [<code>{{clientInfo.memory.free_memory}} Mb</code> free ]

                         <div class="progress" style="height:5px;opacity:0.75;" title="Memory Usage">
                          <div class="progress-bar progress-bar-success" role="progressbar"
                          style="width:{{clientInfo.memory.free_memory*100/clientInfo.memory.real_mem_total}}%">
                          </div>

                          <div class="progress-bar progress-bar-danger" role="progressbar"
                          style="width:{{100-(clientInfo.memory.free_memory*100/clientInfo.memory.real_mem_total)}}%">
                          </div>
                        </div>

                                                </td>
                                        </tr>

                                        <tr>
                                                <td>Disk</td>
                                                <td><code>{{clientInfo.disk.percent}}%</code>
                                                [<code>{{round(clientInfo.disk.free/1024/1024/1024, 2)}} Gb</code> free]

                 <div class="progress" style="height:5px;opacity:0.75" title="Disk Usage">
                  <div class="progress-bar progress-bar-success" role="progressbar"
                  style="width:{{clientInfo.disk.free*100/clientInfo.disk.total}}%">
                  </div>

                  <div class="progress-bar progress-bar-danger" role="progressbar"
                  style="width:{{100-(clientInfo.disk.free*100/clientInfo.disk.total)}}%">
                  </div>
                </div>


                                                </td>

                                        </tr>
                        <tr>

                                <td>Renderes</td><td>
                        <form role="form">
                                            <div class="checkbox"
                                            ng-class="{'checkbox-success':_.contains(clientInfo.render_tools, 'prman')}" >
                                                <input type="checkbox" id="prmanchb"
                                                name="prmanchb" ng-checked="_.contains(clientInfo.render_tools, 'prman')" disabled>
                                                <label for="prmanchb"> Prman</label>
                                            </div>
                                            <div class="checkbox"
                                            ng-class="{'checkbox-success':_.contains(clientInfo.render_tools, 'renderdl')}" >
                                                <input type="checkbox" id="3dlchb"
                                                name="3dlchb" ng-checked="_.contains(clientInfo.render_tools, 'renderdl')" disabled>
                                                <label for="3dlchb"> 3delight</label>
                                            </div>
                                            <div class="checkbox"
                                            ng-class="{'checkbox-success':_.contains(clientInfo.render_tools, 'Maya')}" >
                                                <input type="checkbox" id="mayachb"
                                                name="mayachb" ng-checked="_.contains(clientInfo.render_tools, 'maya')" disabled>
                                                <label for="mayachb"> Maya</label>
                                            </div>
                                            <div class="checkbox"
                                            ng-class="{'checkbox-success':_.contains(clientInfo.render_tools, 'Nuke')}" >
                                                <input type="checkbox" id="nukechb"
                                                name="nukechb" ng-checked="_.contains(clientInfo.render_tools, 'Nuke')" disabled>
                                                <label for="nukechb"> Nuke</label>
                                            </div>
                        </form>

                                </td>

                        </tr>


                                </table>




                        </div>
                        <div class="panel-footer">

                <span ng-show="clientInfo.qmark && clientInfo.render_tools.length>0"
                class="text-success"><i class="fa fa-check"></i> Client has needed tools.</span>
                <span ng-hide="clientInfo.qmark && clientInfo.render_tools.length>0"
                class="text-warning"><i class="fa fa-info"></i> Client not ready yet!</span>
                <br/>
                <span ng-show="options.workerPing==true"
                class="text-success"><i class="fa fa-circle"></i> Worker is up and running</span>
                <span ng-show="options.workerPing==false"
                class="text-danger"><i class="fa fa-circle"></i> Worker is DOWN!</span>

                        </div>
                </div>
        </div>

<div id="square" class="col-md-8" ng-if="server_status==='success'">

  <ul class="nav nav-tabs" role="tablist">
    <li role="presentation" class="active">
            <a href="#queue" aria-controls="queue" role="tab"
                    data-toggle="tab"><em class="fa fa-stack-exchange"></em> Queue</a></li>
    <li role="presentation">
            <a href="#my_machine" aria-controls="my_machine" role="tab"
                    data-toggle="tab"><em class="fa fa-desktop"></em> My Machine</a></li>
    <li role="presentation" >
            <a href="#server" aria-controls="server" role="tab"
                    data-toggle="tab"><em class="fa fa-database"></em> Farm Status</a></li>
    <li role="presentation" >
            <a href="#settings" aria-controls="settings" role="tab"
                    data-toggle="tab"><em class="fa fa-gear"></em> Settings</a></li>
  </ul>

  <div class="tab-content">

            <div role="tabpanel" class="tab-pane active" id="queue">
                <div ng-include="'static/templates/client/queue.html'"></div>
            </div>

            <div role="tabpanel" class="tab-pane" id="my_machine">
                <div ng-include="'static/templates/client/my_machine.html'"></div>
            </div>
            <div role="tabpanel" class="tab-pane" id="server">
                <div ng-include="'static/templates/client/server.html'"></div>
            </div>
            <div role="tabpanel" class="tab-pane" id="settings">
                <div ng-include="'static/templates/client/settings.html'"></div>
            </div>

        </div>
</div>
      </div>



</div>
