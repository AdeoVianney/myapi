/* Global variables */
def manifests_folder = "./install/manifests"
def new_project = true
def url = ''
def project_name = 'myapi'
def job_name = 'myapi'

node ("python27") {
  /* Source git */
  stage("Git clone"){
    deleteDir()
    checkout scm
    url = sh(returnStdout: true, script: 'git config remote.origin.url').trim()
  }

  /* Common services */
  stage("Deploy route + service + redis"){
    openshift.withCluster() {
      openshift.withProject( ) {
        def models = openshift.process("-f", "${manifests_folder}/services.yaml",
          "-p", "GIT_BRANCH=${env.GIT_BRANCH}"
        )
        def created = openshift.apply( models )
      }
    }
  }

  /* API front */
  stage("Build and deploy api front"){
    openshift.withCluster() {
      openshift.withProject() {
        def api_tpl = openshift.process("-f", "${manifests_folder}/api.yaml",
          "-p", "GIT_URL=" + url,
          "-p", "GIT_BRANCH=${env.GIT_BRANCH}"
        )
        def api_created = openshift.apply( api_tpl )
        def api_result = api_created.narrow("bc").startBuild()
        def api_logs = api_result.logs("-f")
      }
    }
  }

  /* Consumers */
  def consumers = []
  findFiles().findAll({ return (it.directory && it.name.contains("consumer-")) }).each{
      consumers << it.name.split("-")[1]
  }
  consumers.each { consumer ->
    stage("Build and deploy ${consumer} consumer"){
      openshift.withCluster() {
        openshift.withProject() {
          def consumer_tpl = openshift.process("-f", "${manifests_folder}/consumer.yaml",
            "-p", "CONSUMER_NAME=" + consumer,
            "-p", "GIT_URL=" + url,
            "-p", "GIT_BRANCH=${env.GIT_BRANCH}"
          )
          def consumer_created = openshift.apply( consumer_tpl )
          def consumer_result = consumer_created.narrow("bc").startBuild()
          def consumer_logs = consumer_result.logs("-f")
        }
      }
    }
  }

  /* Deploy check */
  stage("Check deployments completion"){
    openshift.withCluster() {
      openshift.withProject() {
        timeout(10) {
          def dc = openshift.selector('dc', [
            app: "${env.GIT_BRANCH}",
            branch: "${env.GIT_BRANCH}"
          ])
          dc.withEach {
            def name = it.name().split('/')last()
            def latestDeploymentVersion = openshift.selector('dc', name).object().status.latestVersion
            def rc = openshift.selector('rc', "${name}-${latestDeploymentVersion}")
            rc.untilEach(1){
                def rcMap = it.object()
                return (rcMap.status.replicas.equals(rcMap.status.readyReplicas))
            }
          }
        }
      }
    }
  }
  stage("Run test"){
    println "Run test"
  }
  if ( env.GIT_BRANCH == "master" ) {
    stage("Promote to the next environment"){
      println "Promote the app !!"
    }
  }
}