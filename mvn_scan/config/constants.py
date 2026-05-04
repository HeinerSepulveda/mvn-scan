## FILES ##
PATH_FOLDER = ".mvnScan"
CONFIG_FILE = "config.json"
NAME_DB = "mvn_scan.db"

## URL´s ##
API_SEARCH_MAVEN = "https://central.sonatype.com/api/internal/browse/components"
API_COMPONENT_MAVEN = "https://central.sonatype.com/api/internal/component/details/ossindex?retries=1"
API_DEPENDENCIES_MAVEN = "https://central.sonatype.com/api/internal/browse/dependencies"
URL_MAVEN_CENTRAL_REPO = "https://central.sonatype.com/artifact/"
API_URL_COMPONENT = "https://ossindex.sonatype.org/api/v3/component-report"
URL_NIST = "https://web.nvd.nist.gov/view/vuln/detail?vulnId"
TIME = int(180/0.1)

CONFIG_API_SONATYPE = {
    "api_token": None
}