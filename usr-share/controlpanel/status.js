function init_status_table(domainId, repositoryGroupId, repositoryId) {
    $("#status-table").DataTable({
        "ajax": "/status/data/status?" + $.param({
            domainId: domainId,
            repositoryGroupId: repositoryGroupId,
            repositoryId: repositoryId})
    });
}
