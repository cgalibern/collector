import gluon.contrib.simplejson as sjson
from applications.init.modules import gittrack

def report_published_ids():
    q = db.report_team_publication.group_id.belongs(user_group_ids())
    return [r.report_id for r in db(q).select(db.report_team_publication.report_id)]

def report_published(report_id):
    if 'Manager' in user_groups():
        return
    q = db.report_team_publication.group_id.belongs(user_group_ids())
    if db(q).count() == 0:
        raise Exception("You are not allowed to access the report %s" % str(report_id))

def report_responsible(report_id):
    if 'Manager' in user_groups():
        return
    q = db.report_team_responsible.group_id.belongs(user_group_ids())
    if db(q).count() == 0:
        raise Exception("You are not allowed to do this operation on the report %s" % str(report_id))

def lib_reports_add_default_team_responsible(report_id):
    group_id = user_default_group_id()
    db.report_team_responsible.insert(report_id=report_id, group_id=group_id)

def lib_reports_add_default_team_publication(report_id):
    group_id = user_default_group_id()
    db.report_team_publication.insert(report_id=report_id, group_id=group_id)

def lib_reports_add_to_git(report_id, content):
    o = gittrack.gittrack(otype='reports')
    r = o.commit(report_id, content, author=user_name(email=True))

def lib_reports_revision(report_id, cid):
    o = gittrack.gittrack(otype='reports')
    data = o.lstree_data(cid, report_id)
    oid = data[0]["oid"]
    return {"data": o.show_file_unvalidated(cid, oid, report_id)}

def lib_reports_revisions(report_id):
    o = gittrack.gittrack(otype='reports')
    r = o.timeline([report_id])
    return {"data": r}

def lib_reports_diff(report_id, cid, other=None):
    o = gittrack.gittrack(otype='reports')
    if other:
        r = o.diff_cids(report_id, cid, other, filename="reports")
    else:
        r = o.show(cid, report_id, numstat=True)
    return {"data": r}

def lib_reports_rollback(report_id, cid):
    o = gittrack.gittrack(otype='reports')
    r = o.rollback(report_id, cid, author=user_name(email=True))
    row = db(db.reports.id == report_id).select().first()
    here_d = os.path.dirname(__file__)
    collect_d = os.path.join(here_d, '..', 'private', 'reports')
    with open(collect_d+"/"+report_id+"/reports", "r") as myfile:
        data=myfile.read()
    row.update_record(report_yaml=data)

def get_report_id(report_id):
    try:
        report_id = int(report_id)
        return report_id
    except ValueError:
        pass
    q = db.reports.report_name == report_id
    report = db(q).select().first()
    if report is None:
        return
    return report.id

def report_responsible(report_id):
    try:
        check_privilege("ReportsManager")
        return True
    except:
        return False


