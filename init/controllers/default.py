# coding: utf8

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

@auth.requires_login()
def service_action():
    action = request.vars.select_action
    request.vars.select_action = 'choose'

    if action is None or action == '' or action == 'choose':
        return

    ids = ([])
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        ids += ([key[6:]])

    if len(ids) == 0:
        response.flash = "no target to execute %s on"%action
        return

    sql = """select m.mon_nodname, m.mon_svcname
             from v_svcmon m
             join v_apps_flat a on m.svc_app=a.app
             where m.id in (%(ids)s)
             and responsible='%(user)s'
             group by m.mon_nodname, m.mon_svcname
          """%dict(ids=','.join(ids),
                   user=user_name())
    rows = db.executesql(sql)

    from subprocess import Popen
    def do_select_action(node, svc, action):
        cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                      '-o', 'ForwardX11=no',
                      '-o', 'PasswordAuthentication=no',
               'opensvc@'+node,
               '--',
               'sudo', '/opt/opensvc/bin/svcmgr', '--service', svc, action]
        process = Popen(cmd, stdin=None, stdout=None, close_fds=True)
        #process.communicate()

    for row in rows:
        do_select_action(row[0], row[1], action)

    response.flash = T("launched %(action)s on %(n)d services", dict(
                       n=len(rows), action=action))

@auth.requires_login()
def index():
    toggle_db_filters()

    now = datetime.datetime.now()
    one_days_ago = now - datetime.timedelta(days=1)
    tmo = now - datetime.timedelta(minutes=15)

    query = db.v_svcmon.mon_frozen==1
    query &= _where(None, 'v_svcmon', domain_perms(), 'mon_nodname')
    query = apply_db_filters(query, 'v_svcmon')
    frozen = db(query).select(db.v_svcmon.mon_svcname, db.v_svcmon.mon_nodname,
                              orderby=db.v_svcmon.mon_svcname)

    query = ~db.svcmon.mon_nodname.belongs(db()._select(db.nodes.nodename))
    query &= _where(None, 'svcmon', domain_perms(), 'mon_nodname')
    nodeswithoutasset = db(query).select(db.svcmon.mon_nodname, groupby=db.svcmon.mon_nodname,)

    query = db.v_svcmon.mon_updated<tmo
    query &= _where(None, 'v_svcmon', domain_perms(), 'mon_svcname')
    query = apply_db_filters(query, 'v_svcmon')
    svcnotupdated = db(query).select(orderby=~db.v_svcmon.mon_updated, limitby=(0,50))

    query = db.svcmon_log.mon_end>one_days_ago
    query &= db.svcmon_log.mon_svcname==db.v_svcmon.mon_svcname
    query &= db.svcmon_log.mon_nodname==db.v_svcmon.mon_nodname
    query &= _where(None, 'svcmon_log', domain_perms(), 'mon_svcname')
    query = apply_db_filters(query, 'v_svcmon')
    lastchanges = db(query).select(orderby=~db.svcmon_log.mon_begin, limitby=(0,20))

    query = (db.v_svcmon.err>0)
    query &= _where(None, 'v_svcmon', domain_perms(), 'mon_svcname')
    query = apply_db_filters(query, 'v_svcmon')
    svcwitherrors = db(query).select(orderby=~db.v_svcmon.err, groupby=db.v_svcmon.mon_svcname)

    query = (~db.v_svc_group_status.groupstatus.like("up,%"))
    query &= (~db.v_svc_group_status.groupstatus.like("%,up,%"))
    query &= (~db.v_svc_group_status.groupstatus.like("%,up"))
    query &= (db.v_svc_group_status.groupstatus!="up")
    query &= _where(None, 'v_svc_group_status', domain_perms(), 'svcname')
    query &= db.v_svc_group_status.svcname==db.v_svcmon.mon_svcname
    query = apply_db_filters(query, 'v_svcmon')
    svcnotup = db(query).select(groupby=db.v_svc_group_status.svcname, orderby=db.v_svc_group_status.svcname)

    query = (db.v_svcmon.svc_autostart==db.v_svcmon.mon_nodname)
    query &= ((db.v_svcmon.mon_overallstatus!="up")|(db.v_svcmon.mon_updated<tmo))
    query &= _where(None, 'v_svcmon', domain_perms(), 'mon_svcname')
    query = apply_db_filters(query, 'v_svcmon')
    svcnotonprimary = db(query).select()

    query = (db.v_apps.responsibles==None)
    query |= (db.v_apps.responsibles=="")
    appwithoutresp = db(query).select(db.v_apps.app)

    query = db.v_nodes.warranty_end < now + datetime.timedelta(days=30)
    query &= db.v_nodes.warranty_end != "0000-00-00 00:00:00"
    query &= db.v_nodes.warranty_end is not None
    query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
    query = apply_db_filters(query, 'v_nodes')
    warrantyend = db(query).select(db.v_nodes.nodename,
                                    db.v_nodes.warranty_end,
                                    orderby=db.v_nodes.warranty_end
                                   )

    warn = (db.obsolescence.obs_warn_date!=None)&(db.obsolescence.obs_warn_date!="0000-00-00")&(db.obsolescence.obs_warn_date<now)
    alert = (db.obsolescence.obs_alert_date==None)|(db.obsolescence.obs_alert_date=="0000-00-00")|(db.obsolescence.obs_alert_date>=now)
    query = warn & alert
    query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
    query = apply_db_filters(query, 'v_nodes')
    join = db.obsolescence.obs_type=="os"
    join &= db.obsolescence.obs_name==db.v_nodes.os_concat
    obsoswarn = db(query).select(db.v_nodes.nodename,
                                 db.obsolescence.obs_name,
                                 db.obsolescence.obs_warn_date,
                                 left=db.v_nodes.on(join),
                                 orderby=db.obsolescence.obs_warn_date|db.v_nodes.nodename
                                )

    query = (db.obsolescence.obs_alert_date!=None)&(db.obsolescence.obs_alert_date!="0000-00-00")&(db.obsolescence.obs_alert_date<now)
    query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
    query = apply_db_filters(query, 'v_nodes')
    join = db.obsolescence.obs_type=="os"
    join &= db.obsolescence.obs_name==db.v_nodes.os_concat
    obsosalert = db(query).select(db.v_nodes.nodename,
                                 db.obsolescence.obs_name,
                                 db.obsolescence.obs_alert_date,
                                 left=db.v_nodes.on(join),
                                 orderby=db.obsolescence.obs_alert_date|db.v_nodes.nodename
                                )

    warn = (db.obsolescence.obs_warn_date!=None)&(db.obsolescence.obs_warn_date!="0000-00-00")&(db.obsolescence.obs_warn_date<now)
    alert = (db.obsolescence.obs_alert_date==None)|(db.obsolescence.obs_alert_date=="0000-00-00")|(db.obsolescence.obs_alert_date>=now)
    query = warn & alert
    query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
    query = apply_db_filters(query, 'v_nodes')
    join = db.obsolescence.obs_type=="hw"
    join &= db.obsolescence.obs_name==db.v_nodes.model
    obshwwarn = db(query).select(db.v_nodes.nodename,
                                 db.obsolescence.obs_name,
                                 db.obsolescence.obs_warn_date,
                                 left=db.v_nodes.on(join),
                                 orderby=db.obsolescence.obs_warn_date|db.v_nodes.nodename
                                )

    query = (db.obsolescence.obs_alert_date!=None)&(db.obsolescence.obs_alert_date!="0000-00-00")&(db.obsolescence.obs_alert_date<now)
    query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
    query = apply_db_filters(query, 'v_nodes')
    join = db.obsolescence.obs_type=="hw"
    join &= db.obsolescence.obs_name==db.v_nodes.model
    obshwalert = db(query).select(db.v_nodes.nodename,
                                 db.obsolescence.obs_name,
                                 db.obsolescence.obs_alert_date,
                                 left=db.v_nodes.on(join),
                                 orderby=db.obsolescence.obs_alert_date|db.v_nodes.nodename
                                )

    rows = db(db.v_users.id==session.auth.user.id).select(db.v_users.manager)
    if len(rows) == 1 and rows[0].manager == 1:
        query = (db.obsolescence.obs_warn_date==None)|(db.obsolescence.obs_warn_date=="0000-00-00")
        query &= (db.v_nodes.os_concat==db.obsolescence.obs_name)|(db.v_nodes.model==db.obsolescence.obs_name)
        query &= (~db.v_nodes.model.like("%virtual%"))
        query &= (~db.v_nodes.model.like("%virtuel%"))
        query &= (~db.v_nodes.model.like("%cluster%"))
        query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
        query = apply_db_filters(query, 'v_nodes')
        rows = db(query).select(db.obsolescence.obs_name, groupby=db.obsolescence.obs_name)
        obswarnmiss = len(rows)

        query = (db.obsolescence.obs_alert_date==None)|(db.obsolescence.obs_alert_date=="0000-00-00")
        query &= (db.v_nodes.os_concat==db.obsolescence.obs_name)|(db.v_nodes.model==db.obsolescence.obs_name)
        query &= (~db.v_nodes.model.like("%virtual%"))
        query &= (~db.v_nodes.model.like("%virtuel%"))
        query &= (~db.v_nodes.model.like("%cluster%"))
        query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
        query = apply_db_filters(query, 'v_nodes')
        rows = db(query).select(db.obsolescence.obs_name, groupby=db.obsolescence.obs_name)
        obsalertmiss = len(rows)
    else:
        obswarnmiss = 0
        obsalertmiss = 0

    pkgdiff = {}
    clusters = {}
    query = _where(None, 'v_svc_group_status', domain_perms(), 'svcname')
    query &= db.v_svc_group_status.svcname==db.v_svcmon.mon_svcname
    query = apply_db_filters(query, 'v_svcmon')
    rows = db(query).select(db.v_svc_group_status.nodes, distinct=True)
    for row in rows:
        nodes = row.nodes.split(',')
        s = set(nodes)
        if s in clusters.values():
            continue
        clusters[row.nodes] = set(nodes)
        n = len(nodes)
        if n == 1:
            continue
        nodes.sort()
        key = ','.join(nodes)
        if key in pkgdiff:
            continue
        sql = """select count(id) from (
                   select *,count(pkg_nodename) as c
                   from packages
                   where pkg_nodename in (%(nodes)s)
                   group by pkg_name,pkg_version,pkg_arch
                   order by pkg_name,pkg_version,pkg_arch
                 ) as t
                 where t.c!=%(n)s;
              """%dict(n=n, nodes=','.join(map(repr, nodes)))
        x = db.executesql(sql)
        if len(x) != 1 or len(x[0]) != 1 or x[0][0] == 0:
            continue
        pkgdiff[key] = x[0][0]

    q = db.v_stats_netdev_err_avg_last_day.avgrxerrps > 0
    q |= db.v_stats_netdev_err_avg_last_day.avgtxerrps > 0
    q |= db.v_stats_netdev_err_avg_last_day.avgcollps > 0
    q |= db.v_stats_netdev_err_avg_last_day.avgrxdropps > 0
    q |= db.v_stats_netdev_err_avg_last_day.avgtxdropps > 0
    query = _where(None, 'v_stats_netdev_err_avg_last_day', domain_perms(), 'nodename')
    query &= db.v_stats_netdev_err_avg_last_day.nodename==db.v_nodes.nodename
    query = apply_db_filters(query, 'v_nodes')
    query &= q
    netdeverrs = db(query).select()

    q = db.v_checks.chk_value < db.v_checks.chk_low
    q |= db.v_checks.chk_value > db.v_checks.chk_high
    query = _where(None, 'v_checks', domain_perms(), 'chk_nodename')
    query &= q
    query &= db.v_checks.chk_nodename==db.v_nodes.nodename
    query = apply_db_filters(query, 'v_nodes')
    checks = db(query).select()

    return dict(svcnotupdated=svcnotupdated,
                frozen=frozen,
                nodeswithoutasset=nodeswithoutasset,
                lastchanges=lastchanges,
                svcwitherrors=svcwitherrors,
                svcnotonprimary=svcnotonprimary,
                appwithoutresp=appwithoutresp,
                warrantyend=warrantyend,
                obsoswarn=obsoswarn,
                obsosalert=obsosalert,
                obshwwarn=obshwwarn,
                obshwalert=obshwalert,
                obswarnmiss=obswarnmiss,
                obsalertmiss=obsalertmiss,
                svcnotup=svcnotup,
                active_filters=active_db_filters('v_svcmon'),
                available_filters=avail_db_filters('v_svcmon'),
                pkgdiff=pkgdiff,
                netdeverrs=netdeverrs,
                checks=checks,
               )

@auth.requires_login()
def envfile(svcname):
    query = _where(None, 'services', svcname, 'svc_name')
    query &= _where(None, 'v_svcmon', domain_perms(), 'svc_name')
    rows = db(query).select()
    if len(rows) == 0:
        return "None"
    #return dict(svc=rows[0])
    envfile = rows[0]['services']['svc_envfile']
    if envfile is None:
        return "None"
    return DIV(
             P(T("updated: %(upd)s",dict(
                     upd=rows[0]['services']['updated']
                   ),
                ),
                _style='text-align:center',
             ),
             PRE(envfile.replace('\\n','\n'), _style="text-align:left"),
           )

@auth.requires_login()
def svcmon():
    service_action()

    d1 = v_svcmon_columns()
    d2 = v_nodes_columns()
    for k in d2:
        d2[k]['pos'] += 50
        d2[k]['display'] = False

    del(d2['nodename'])
    columns = d1.copy()
    columns.update(d2)

    def _sort_cols(x, y):
        return cmp(columns[x]['pos'], columns[y]['pos'])
    colkeys = columns.keys()
    colkeys.sort(_sort_cols)
    __update_columns(columns, 'svcmon')

    o = db.v_svcmon.mon_svcname
    o |= ~db.v_svcmon.mon_overallstatus
    o |= ~db.v_svcmon.mon_nodtype
    o |= db.v_svcmon.mon_nodname

    toggle_db_filters()

    query = _where(None, 'v_svcmon', domain_perms(), 'mon_nodname')
    for key in columns.keys():
        if key not in request.vars.keys():
            continue
        query &= _where(None, 'v_svcmon', request.vars[key], key)

    query &= _where(None, 'v_svcmon', request.vars.svc_app, 'svc_app')
    query &= _where(None, 'v_svcmon', request.vars.responsibles, 'responsibles')
    query &= _where(None, 'v_svcmon', request.vars.svc_autostart, 'svc_autostart')
    query &= _where(None, 'v_svcmon', request.vars.svc_containertype, 'svc_containertype')
    query &= _where(None, 'v_svcmon', request.vars.svc_vcpus, 'svc_vcpus')
    query &= _where(None, 'v_svcmon', request.vars.svc_vmem, 'svc_vmem')

    query = apply_db_filters(query, 'v_svcmon')

    (start, end, nav) = _pagination(request, query)
    if start == 0 and end == 0:
        rows = db(query).select(orderby=o)
    else:
        rows = db(query).select(limitby=(start,end), orderby=o)

    msgs = db(db.svcmessages.id>0).select()
    svcmsg = [msg.msg_svcname for msg in msgs if len(msg.msg_body)>0]

    return dict(columns=columns, colkeys=colkeys, actions=rows,
                services=rows,
                nav=nav,
                svcmsg=svcmsg,
                active_filters=active_db_filters('v_svcmon'),
                available_filters=avail_db_filters('v_svcmon'),
               )

class viz(object):
    import os
    vizdir = os.path.join(os.getcwd(), 'applications', 'init', 'static')
    vizprefix = 'tempviz'
    loc = {
        'country': {},
        'city': {},
        'building': {},
        'floor': {},
        'room': {},
        'rack': {},
    }
    svcclu = {}
    services = set([])
    resources = {}
    nodes = set([])
    disks = {}
    cdg = {}
    cdgdg = {}
    vidcdg = {}
    array = {}
    arrayinfo = {}
    disk2svc = set([])
    node2disk = set([])
    node2svc = set([])
    data = ""
    img_node = 'applications'+str(URL(r=request,c='static',f='node.png'))
    img_disk = 'applications'+str(URL(r=request,c='static',f='hd.png'))

    def __str__(self):
        buff = """
        graph G {
                //size=12;
                rankdir=LR;
                ranksep=2.5;
                //nodesep = 0.1;
                //sep=0.1;
                splines=false;
                penwidth=1;
                //center=true;
                fontsize=8;
                compound=true;
                node [shape=plaintext, fontsize=8];
                edge [fontsize=8];
                bgcolor=white;

        """
        self.add_services()
        self.add_arrays()
        self.add_citys()
        #self.rank(['cluster_'+s for s in self.array])
        #self.rank(self.services)
        buff += self.data
        buff += "}"
        return buff

    def write(self, type):
        import tempfile
        f = tempfile.NamedTemporaryFile(dir=self.vizdir, prefix=self.vizprefix)
        f.close()
        dot = f.name + '.dot'
        f = open(dot, 'w')
        f.write(str(self))
        f.close()
        if type == 'dot':
            return dot
        from subprocess import Popen
        dst = f.name + '.' + type
        cmd = [ 'dot', '-T'+type, '-o', dst, dot ]
        process = Popen(cmd, stdout=None, stderr=None)
        process.communicate()
        return dst

    def viz_cron_cleanup(self):
        """ unlink static/tempviz*.png
        """
        import os
        import glob
        files = []
        for name in glob.glob(os.path.join(self.vizdir, self.vizprefix+'*.png')):
            files.append(name)
            os.unlink(name)
        for name in glob.glob(os.path.join(self.vizdir, self.vizprefix+'*.dot')):
            files.append(name)
            os.unlink(name)
        for name in glob.glob(os.path.join(self.vizdir, 'stats_*_[0-9]*.png')):
            files.append(name)
            os.unlink(name)
        for name in glob.glob(os.path.join(self.vizdir, 'stat_*_[0-9]*.png')):
            files.append(name)
            os.unlink(name)
        for name in glob.glob(os.path.join(self.vizdir, 'stats_*_[0-9]*.svg')):
            files.append(name)
            os.unlink(name)
        return files

    def __init__(self):
        pass

    def vid_svc(self, svc, nodename):
        return "svc_"+nodename.replace(".", "_").replace("-", "_")+"_"+svc.replace(".", "_").replace("-", "_")

    def vid_svc_dg(self, svc, dg):
        return "dg_"+svc.replace(".", "_").replace("-", "_")+"_"+dg

    def vid_node(self, node):
        return 'node_'+node.replace(".", "_").replace("-", "_")

    def vid_disk(self, id):
        return 'disk_'+str(id).replace(".", "_").replace("-", "_")

    def vid_loc(self, id):
        return str(id).replace(".", "_").replace("-", "_").replace(" ", "_")

    def add_service(self, svc):
        vid = self.vid_svc(svc.svc_name, svc.mon_nodname)
        if vid in self.services: return
        self.services = set([vid])
        if svc.mon_overallstatus == "warn":
            color = "orange"
        elif svc.mon_overallstatus == "up":
            color = "green"
        else:
            color = "grey"
        servicesdata = r"""
        %(v)s [label="%(s)s", style="rounded,filled", fillcolor="%(color)s", fontsize="12"];
        """%(dict(v=vid, s=svc.svc_name, color=color))
        if svc.mon_nodname not in self.svcclu:
            self.svcclu[svc.mon_nodname] = {}
        if svc.mon_overallstatus not in self.svcclu[svc.mon_nodname]:
            self.svcclu[svc.mon_nodname][svc.mon_overallstatus] = set([])
        self.svcclu[svc.mon_nodname][svc.mon_overallstatus] |= set([servicesdata])

    def add_node(self, svc):
        vid = self.vid_node(svc.mon_nodname)
        if vid in self.nodes: return
        self.nodes |= set([vid])
        if svc.loc_city not in self.loc['city']:
            self.loc['city'][svc.loc_city] = ""
        self.loc['city'][svc.loc_city] += r"""
        %(v)s [label="", image="%(img)s"];
        subgraph cluster_%(v)s {fontsize=8; penwidth=0; label="%(n)s\n%(model)s\n%(mem)s MB"; labelloc=b; %(v)s};
        """%(dict(v=vid, n=svc.mon_nodname, model=svc.model, mem=svc.mem_bytes, img=self.img_node))

    def add_disk(self, id, disk, size="", vendor="", model="", arrayid="", devid=""):
        vid = self.vid_disk(id)
        if disk in self.disks: return
        self.disks[disk]= vid
        self.add_array(vid, arrayid, vendor, model)
        self.data += r"""
        %(id)s [label="%(name)s\n%(devid)s\n%(size)s GB", image="%(img)s"];
        """%(dict(id=vid, name=disk, size=size, img=self.img_disk, devid=devid))

    def add_array(self, vid, arrayid="", vendor="", model=""):
        if arrayid == "" or arrayid is None:
            return
        if arrayid not in self.array:
            self.array[arrayid] = set([vid])
        else:
            self.array[arrayid] |= set([vid])
        if arrayid not in self.arrayinfo:
            title = arrayid
            self.arrayinfo[arrayid] = r"%s\n%s - %s"%(title, vendor.strip(), model.strip())

    def add_services(self):
        for n in self.svcclu:
            for s in self.svcclu[n]:
                self.data += r"""subgraph cluster_%(n)s_%(s)s {penwidth=0;
                %(svcs)s
        };"""%dict(n=n.replace('.','_').replace('-','_'), s=s.replace(' ','_'), svcs=''.join(self.svcclu[n][s]))

    def add_citys(self):
        for a in self.loc['city']:
            self.data += r"""
        subgraph cluster_%(a)s {label="%(l)s"; color=grey; style=rounded; fontsize=12; %(n)s};
        """%(dict(a=self.vid_loc(a), l=a, n=self.loc['city'][a]))

    def add_arrays(self):
        for a in self.array:
            if a is None:
                continue
            nodes = [self.cdg_cluster(v) for v in self.array[a] if "cdg_" in v]
            nodes += [v for v in self.array[a] if "cdg_" not in v]
            self.data += r"""
        subgraph cluster_%(a)s {label="%(l)s"; fillcolor=lightgrey; style="rounded,filled"; fontsize=12; %(disks)s};
        """%(dict(a=a.replace("-","_"), l=self.arrayinfo[a], disks=';'.join(nodes)))

    def rank(self, list):
        return """{ rank=same; %s };
               """%'; '.join(list)

    def add_node2svc(self, svc):
        vid1 = self.vid_node(svc.mon_nodname)
        vid2 = self.vid_svc(svc.svc_name, svc.mon_nodname)
        key = vid1+vid2
        if key in self.node2svc: return
        if svc.mon_overallstatus == "up":
            color = "darkgreen"
        else:
            color = "grey"
        self.node2svc |= set([key])
        self.data += """
        edge [color=%(c)s, label="", arrowsize=0, penwidth=1]; %(n)s -- %(d)s;
        """%(dict(c=color, n=vid1, d=vid2))

    def add_disk2svc(self, disk, svc, dg=""):
        vid1 = self.disks[disk]
        if dg == "":
            vid2 = self.vid_svc(svc.svc_name, svc.mon_nodname)
        else:
            vid2 = self.vid_svc_dg(svc.svc_name, dg)
        key = vid1+vid2
        if key in self.disk2svc: return
        self.disk2svc |= set([key])
        if svc.mon_overallstatus == "up":
            color = "darkgreen"
        else:
            color = "grey"
        self.data += """
        edge [color=%(c)s, label="", arrowsize=0, penwidth=1]; %(s)s -- %(d)s;
        """%(dict(c=color, d=vid1, s=vid2))

    def cdg_cluster(self, cdg):
        if cdg not in self.cdg or len(self.cdg[cdg]) == 0:
            return ""
        if cdg in self.cdgdg:
            dg = self.cdgdg[cdg]
        else:
            dg = cdg

        return r"""
            %(cdg)s [shape="plaintext"; label=<<table color="white"
            cellspacing="0" cellpadding="2" cellborder="1">
            <tr><td colspan="3">%(dg)s</td></tr>
            <tr><td>wwid</td><td>devid</td><td>size</td></tr>
            %(n)s
            </table>>]"""%dict(dg=dg, cdg=cdg, n=''.join(self.cdg[cdg]))

    def vid_cdg(self, d):
        key = d.disk_arrayid,d.disk_svcname,d.disk_dg
        cdg = 'cdg_'+str(len(self.vidcdg))
        if key not in self.vidcdg:
            self.vidcdg[key] = cdg
            self.cdgdg[cdg] = d.disk_dg
        return self.vidcdg[key]

    def add_dgdisk(self, d):
        cdg = self.vid_cdg(d)
        vid = self.vid_disk(d.id)
        self.disks[d.disk_id] = vid
        self.add_array(cdg, d.disk_arrayid, d.disk_vendor, d.disk_model)
        if cdg not in self.cdg:
            self.cdg[cdg] = []
        label="<tr><td>%(name)s</td><td>%(devid)s</td><td>%(size)s GB</td></tr>"%(dict(id=vid, name=d.disk_id, size=d.disk_size, img=self.img_disk, devid=d.disk_devid))
        if label not in self.cdg[cdg]:
            self.cdg[cdg].append(label)

    def add_dg2svc(self, cdg, svc, dg=""):
        vid1 = cdg
        if dg == "":
            vid2 = self.vid_svc(svc.svc_name, svc.mon_nodname)
        else:
            vid2 = self.vid_svc_dg(svc.svc_name, dg)
        key = cdg+vid2
        if key in self.disk2svc: return
        self.disk2svc |= set([key])
        if svc.mon_overallstatus == "up":
            color = "darkgreen"
        else:
            color = "grey"
        self.data += """
        edge [color=%(c)s, label="", arrowsize=0, penwidth=1]; %(s)s -- %(cdg)s;
        """%(dict(c=color, d=vid1, s=vid2, cdg=cdg))

    def add_disks(self, svc):
        svccdg = set([])
        q = (db.v_svcdisks.disk_svcname==svc.svc_name)
        q &= (db.v_svcdisks.disk_nodename==svc.mon_nodname)
        q &= (db.v_svcdisks.disk_id!="")
        dl = db(q).select()
        if len(dl) == 0:
            disk_id = svc.mon_nodname + "_unknown"
            self.add_disk(svc.mon_nodname, disk_id, size="?")
            self.add_disk2svc(disk_id, svc)
        else:
            for d in dl:
                if d.disk_dg is None or d.disk_dg == "":
                    disk_id = svc.mon_nodname + "_unknown"
                    self.add_disk(svc.mon_nodname, disk_id, size="?")
                    self.add_disk2svc(disk_id, svc)
                else:
                    svccdg |= set([self.vid_cdg(d)])
                    self.add_dgdisk(d)
        for cdg in svccdg:
            self.add_dg2svc(cdg, svc)

def svcmon_viz_img(services):
    v = viz()
    for svc in services:
        v.add_node(svc)
        v.add_disks(svc)
        v.add_service(svc)
        v.add_node2svc(svc)
    fname = v.write('png')
    import os
    img = str(URL(r=request,c='static',f=os.path.basename(fname)))
    return img

def ajax_svcmon_viz():
    s = svcmon()
    img = svcmon_viz_img(s['services'])
    return IMG(_src=img, _border=0)

def svcmon_viz():
    request.vars['perpage'] = 0
    s = svcmon()
    img = svcmon_viz_img(s['services'])
    return dict(s=s['services'], img=img)

def viz_cron_cleanup():
    return viz().viz_cron_cleanup()

def svcmon_csv():
    import gluon.contenttype
    response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
    request.vars['perpage'] = 0
    return str(svcmon()['services'])

@auth.requires_login()
def ajax_res_status():
    svcname = request.vars.mon_svcname
    node = request.vars.node
    return res_status(svcname, node)

def res_status(svcname, node):
    rows = db((db.resmon.svcname==svcname)&(db.resmon.nodename==node)).select(orderby=db.resmon.rid)
    def print_row(row):
        cssclass = 'status_'+row.res_status.replace(" ", "_")
        return (TR(
                 TD(row.rid),
                 TD(row.res_status, _class='%s'%cssclass),
                 TD(row.res_desc),
               ),
               TR(
                 TD(),
                 TD(),
                 TD(PRE(row.res_log)),
               ))
    t = TABLE(
          TR(
            TH('id'),
            TH('status'),
            TH('description'),
          ),
          map(print_row, rows)
    )
    return DIV(
             P(
               H2("%(svc)s@%(node)s"%dict(svc=svcname, node=node),
               _style="text-align:center")
             ),
             t,
             _class="dashboard",
           )

@auth.requires_login()
def ajax_service():
    rowid = request.vars.rowid
    rows = db(db.v_svcmon.mon_svcname==request.vars.node).select()
    viz = svcmon_viz_img(rows)
    if len(rows) == 0:
        return DIV(
                 T("No service information for %(node)s",
                   dict(node=request.vars.node)),
               )

    s = rows[0]
    t_misc = TABLE(
      TR(
        TD(T('opensvc version'), _style='font-style:italic'),
        TD(s['svc_version'])
      ),
      TR(
        TD(T('unacknowledged errors'), _style='font-style:italic'),
        TD(s['err'])
      ),
      TR(
        TD(T('type'), _style='font-style:italic'),
        TD(s['svc_type'])
      ),
      TR(
        TD(T('application'), _style='font-style:italic'),
        TD(s['svc_app'])
      ),
      TR(
        TD(T('comment'), _style='font-style:italic'),
        TD(s['svc_comment'])
      ),
      TR(
        TD(T('last update'), _style='font-style:italic'),
        TD(s['svc_updated'])
      ),
      TR(
        TD(T('container type'), _style='font-style:italic'),
        TD(s['svc_containertype'])
      ),
      TR(
        TD(T('container name'), _style='font-style:italic'),
        TD(s['svc_vmname'])
      ),
      TR(
        TD(T('responsibles'), _style='font-style:italic'),
        TD(s['responsibles'])
      ),
      TR(
        TD(T('responsibles mail'), _style='font-style:italic'),
        TD(s['mailto'])
      ),
      TR(
        TD(T('primary node'), _style='font-style:italic'),
        TD(s['svc_autostart'])
      ),
      TR(
        TD(T('nodes'), _style='font-style:italic'),
        TD(s['svc_nodes'])
      ),
      TR(
        TD(T('drp node'), _style='font-style:italic'),
        TD(s['svc_drpnode'])
      ),
      TR(
        TD(T('drp nodes'), _style='font-style:italic'),
        TD(s['svc_drpnodes'])
      ),
      TR(
        TD(T('vcpus'), _style='font-style:italic'),
        TD(s['svc_vcpus'])
      ),
      TR(
        TD(T('vmem'), _style='font-style:italic'),
        TD(s['svc_vmem'])
      ),
    )

    def print_status_row(row):
        r = DIV(
              H2(row.mon_nodname, _style='text-align:center'),
              svc_status(row),
              _style='float:left; padding:0 1em',
            )
        return r
    status = map(print_status_row, rows)
    t_status = SPAN(
                 status,
               )

    def print_rstatus_row(row):
        r = DIV(
              res_status(row.mon_svcname, row.mon_nodname),
              _style='float:left',
            )
        return r
    rstatus = map(print_rstatus_row, rows)
    t_rstatus = SPAN(
                  rstatus,
                )

    def js(tab, rowid):
        buff = ""
        for i in range(1, 6):
            buff += """getElementById('%(tab)s_%(id)s').style['display']='none';
                       getElementById('li%(tab)s_%(id)s').style['backgroundColor']='#EEE';
                    """%dict(tab='tab'+str(i), id=rowid)
        buff += """getElementById('%(tab)s_%(id)s').style['display']='block';
                   getElementById('li%(tab)s_%(id)s').style['backgroundColor']='orange';
                """%dict(tab=tab, id=rowid)
        return buff


    t = TABLE(
      TR(
        TD(
          UL(
            LI(
              P(
                T("close %(n)s", dict(n=request.vars.node)),
                _class="tab closetab",
                _onclick="""
                    getElementById("tr_id_%(id)s").style['display']='none'
                """%dict(id=rowid),
              ),
            ),
            LI(
              P(
                T("properties"),
                _class="tab",
                _onclick=js('tab1', rowid)
               ),
              _id="litab1_"+str(rowid),
              _style="background-color:orange",
            ),
            LI(P(T("status"), _class="tab", _onclick=js('tab2', rowid)), _id="litab2_"+str(rowid)),
            LI(P(T("resources"), _class="tab", _onclick=js('tab3', rowid)), _id="litab3_"+str(rowid)),
            LI(P(T("env"), _class="tab", _onclick=js('tab4', rowid)), _id="litab4_"+str(rowid)),
            LI(P(T("topology"), _class="tab", _onclick=js('tab5', rowid)), _id="litab5_"+str(rowid)),
            _class="web2py-menu web2py-menu-horizontal",
          ),
          _style="border-bottom:solid 1px orange;padding:1px",
        ),
      ),
      TR(
        TD(
          DIV(
            t_misc,
            _id='tab1_'+str(rowid),
            _class='cloud_shown',
          ),
          DIV(
            t_status,
            _id='tab2_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            t_rstatus,
            _id='tab3_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            envfile(request.vars.node),
            _id='tab4_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            IMG(_src=viz),
            _id='tab5_'+str(rowid),
            _class='cloud',
          ),
        ),
      ),
    )
    return t

class ex(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

#
# XMLRPC
#
#########
@service.xmlrpc
def delete_services(hostid=None):
    if hostid is None:
        return 0
    db(db.services.svc_hostid==hostid).delete()
    db.commit()
    return 0

@service.xmlrpc
def delete_service_list(hostid=None, svcnames=[]):
    if hostid is None or len(svcnames) == 0:
        return 0
    for svcname in svcnames:
        q = (db.services.svc_name==svcname)
        q &= (db.services.svc_hostid==hostid)
        db(q).delete()
        db.commit()
    return 0

@service.xmlrpc
def begin_action(vars, vals):
    sql="""insert delayed into SVCactions (%s) values (%s)""" % (','.join(vars), ','.join(vals))
    db.executesql(sql)
    db.commit()
    return 0

@service.xmlrpc
def res_action(vars, vals):
    upd = []
    for a, b in zip(vars, vals):
        upd.append("%s=%s" % (a, b))
    sql="""insert delayed into SVCactions (%s) values (%s)""" % (','.join(vars), ','.join(vals))
    db.executesql(sql)
    db.commit()
    return 0

@service.xmlrpc
def end_action(vars, vals):
    upd = []
    h = {}
    for a, b in zip(vars, vals):
        h[a] = b
        if a not in ['hostname', 'svcname', 'begin', 'action', 'hostid']:
            upd.append("%s=%s" % (a, b))
    sql="""update SVCactions set %s where hostname=%s and svcname=%s and begin=%s and action=%s""" %\
        (','.join(upd), h['hostname'], h['svcname'], h['begin'], h['action'])
    #raise Exception(sql)
    db.executesql(sql)
    db.commit()
    return 0

def value_wrap(a):
    return "%(a)s=values(%(a)s)"%dict(a=a)

def quote_wrap(x):
    if isinstance(x, (int, long, float, complex)):
        return x
    elif isinstance(x, str) and len(x) == 0:
        return "''"
    elif isinstance(x, str) and x[0] == "'" and x[-1] == "'":
        return x
    elif isinstance(x, str) and x[0] == '"' and x[-1] == '"':
        return x
    else:
        return "'%s'"%str(x).replace("'", '"')

def insert_multiline(table, vars, valsl):
    value_wrap = lambda a: "%(a)s=values(%(a)s)"%dict(a=a)
    line_wrap = lambda x: "(%(x)s)"%dict(x=','.join(map(quote_wrap, x)))
    upd = map(value_wrap, vars)
    lines = map(line_wrap, valsl)
    sql="""insert delayed into %s (%s) values %s on duplicate key update %s""" % (table, ','.join(vars), ','.join(lines), ','.join(upd))
    db.executesql(sql)
    db.commit()

def generic_insert(table, vars, vals):
    if len(vals) == 0:
        return
    elif isinstance(vals[0], list):
        insert_multiline(table, vars, vals)
    else:
        insert_multiline(table, vars, [vals])

@service.xmlrpc
def update_service(vars, vals):
    if 'svc_hostid' not in vars:
        return
    if 'updated' not in vars:
        vars += ['updated']
        vals += [datetime.datetime.now()]
    generic_insert('services', vars, vals)

@service.xmlrpc
def push_checks(vars, vals):
    generic_insert('checks_live', vars, vals)

@service.xmlrpc
def update_asset(vars, vals):
    generic_insert('nodes', vars, vals)

@service.xmlrpc
def res_action_batch(vars, vals):
    generic_insert('SVCactions', vars, vals)

def _resmon_clean(node, svcname):
    if node is None or node == '':
        return 0
    if svcname is None or svcname == '':
        return 0
    q = db.resmon.nodename==node.strip("'")
    q &= db.resmon.svcname==svcname.strip("'")
    db(q).delete()
    db.commit()

@service.xmlrpc
def resmon_update(vars, vals):
    h = {}
    for a,b in zip(vars, vals[0]):
        h[a] = b
    if 'nodename' in h and 'svcname' in h:
        _resmon_clean(h['nodename'], h['svcname'])
    generic_insert('resmon', vars, vals)

@service.xmlrpc
def register_disk(vars, vals):
    generic_insert('svcdisks', vars, vals)

@service.xmlrpc
def register_sync(vars, vals):
    pass

@service.xmlrpc
def register_ip(vars, vals):
    pass

@service.xmlrpc
def register_fs(vars, vals):
    pass

@service.xmlrpc
def insert_stats_cpu(vars, vals):
    generic_insert('stats_cpu', vars, vals)

@service.xmlrpc
def insert_stats_mem_u(vars, vals):
    generic_insert('stats_mem_u', vars, vals)

@service.xmlrpc
def insert_stats_proc(vars, vals):
    generic_insert('stats_proc', vars, vals)

@service.xmlrpc
def insert_stats_swap(vars, vals):
    generic_insert('stats_swap', vars, vals)

@service.xmlrpc
def insert_stats_block(vars, vals):
    generic_insert('stats_block', vars, vals)

@service.xmlrpc
def insert_stats_blockdev(vars, vals):
    generic_insert('stats_blockdev', vars, vals)

@service.xmlrpc
def insert_stats_netdev(vars, vals):
    generic_insert('stats_netdev', vars, vals)

@service.xmlrpc
def insert_stats_netdev_err(vars, vals):
    generic_insert('stats_netdev_err', vars, vals)

@service.xmlrpc
def insert_pkg(vars, vals):
    generic_insert('packages', vars, vals)

@service.xmlrpc
def update_sym_xml(symid, vars, vals):
    import os

    dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
    if not os.path.exists(dir):
        os.makedirs(dir)

    dir = os.path.join(dir, symid)
    if not os.path.exists(dir):
        os.makedirs(dir)

    for a,b in zip(vars, vals):
        a = os.path.join(dir, a)
        try:
            f = open(a, 'w')
            f.write(b)
            f.close()
        except:
            pass

    symmetrix = local_import('symmetrix', reload=True)
    s = symmetrix.Vmax(dir)

    #
    # better to create hashes from the batch rather than
    # during an interactive session
    #
    s.get_sym_all()

    #
    # populate the diskinfo table
    #
    vars = ['disk_id', 'disk_devid', 'disk_arrayid']
    vals = []
    for devname, dev in s.dev.items():
        vals.append([dev.wwn, devname, symid])
    generic_insert('diskinfo', vars, vals)

@service.xmlrpc
def delete_pkg(node):
    if node is None or node == '':
        return 0
    db(db.packages.pkg_nodename==node).delete()
    db.commit()

@service.xmlrpc
def insert_patch(vars, vals):
    generic_insert('patches', vars, vals)

@service.xmlrpc
def delete_patch(node):
    if node is None or node == '':
        return 0
    db(db.patches.patch_nodename==node).delete()
    db.commit()

@service.xmlrpc
def delete_syncs(svcname):
    pass

@service.xmlrpc
def delete_ips(svcname, node):
    pass

@service.xmlrpc
def delete_fss(svcname):
    pass

@service.xmlrpc
def delete_disks(svcname, node):
    if svcname is None or svcname == '':
        return 0
    db((db.svcdisks.disk_svcname==svcname)&(db.svcdisks.disk_nodename==node)).delete()
    db.commit()

@service.xmlrpc
def svcmon_update(vars, vals):
    generic_insert('svcmon', vars, vals)
    h = {}
    for a,b in zip(vars, vals):
        h[a] = b
    tmo = datetime.datetime.strptime(h['mon_updated'].split('.')[0], "%Y-%m-%d %H:%M:%S") - datetime.timedelta(minutes=18)
    query = db.svcmon_log.mon_svcname==h['mon_svcname']
    query &= db.svcmon_log.mon_nodname==h['mon_nodname']
    last = db(query).select(orderby=~db.svcmon_log.id, limitby=(0,1))
    if len(last) == 0:
        _vars = ['mon_begin',
                 'mon_end',
                 'mon_svcname',
                 'mon_nodname',
                 'mon_overallstatus',
                 'mon_ipstatus',
                 'mon_fsstatus',
                 'mon_diskstatus',
                 'mon_containerstatus',
                 'mon_appstatus',
                 'mon_syncstatus']
        _vals = [h['mon_updated'],
                 h['mon_updated'],
                 h['mon_svcname'],
                 h['mon_nodname'],
                 h['mon_overallstatus'],
                 h['mon_ipstatus'],
                 h['mon_fsstatus'],
                 h['mon_diskstatus'],
                 h['mon_containerstatus'],
                 h['mon_appstatus'],
                 h['mon_syncstatus']]
        generic_insert('svcmon_log', _vars, _vals)
    elif last[0].mon_end < tmo:
        _vars = ['mon_begin',
                 'mon_end',
                 'mon_svcname',
                 'mon_nodname',
                 'mon_overallstatus',
                 'mon_ipstatus',
                 'mon_fsstatus',
                 'mon_diskstatus',
                 'mon_containerstatus',
                 'mon_appstatus',
                 'mon_syncstatus']
        _vals = [last[0].mon_end,
                 h['mon_updated'],
                 h['mon_svcname'],
                 h['mon_nodname'],
                 "undef",
                 "undef",
                 "undef",
                 "undef",
                 "undef",
                 "undef",
                 "undef"]
        generic_insert('svcmon_log', _vars, _vals)
        _vars = ['mon_begin',
                 'mon_end',
                 'mon_svcname',
                 'mon_nodname',
                 'mon_overallstatus',
                 'mon_ipstatus',
                 'mon_fsstatus',
                 'mon_diskstatus',
                 'mon_containerstatus',
                 'mon_appstatus',
                 'mon_syncstatus']
        _vals = [h['mon_updated'],
                 h['mon_updated'],
                 h['mon_svcname'],
                 h['mon_nodname'],
                 h['mon_overallstatus'],
                 h['mon_ipstatus'],
                 h['mon_fsstatus'],
                 h['mon_diskstatus'],
                 h['mon_containerstatus'],
                 h['mon_appstatus'],
                 h['mon_syncstatus']]
        generic_insert('svcmon_log', _vars, _vals)
    elif h['mon_overallstatus'] != last[0].mon_overallstatus or \
         h['mon_ipstatus'] != last[0].mon_ipstatus or \
         h['mon_fsstatus'] != last[0].mon_fsstatus or \
         h['mon_diskstatus'] != last[0].mon_diskstatus or \
         h['mon_containerstatus'] != last[0].mon_containerstatus or \
         h['mon_appstatus'] != last[0].mon_appstatus or \
         h['mon_syncstatus'] != last[0].mon_syncstatus:
        _vars = ['mon_begin',
                 'mon_end',
                 'mon_svcname',
                 'mon_nodname',
                 'mon_overallstatus',
                 'mon_ipstatus',
                 'mon_fsstatus',
                 'mon_diskstatus',
                 'mon_containerstatus',
                 'mon_appstatus',
                 'mon_syncstatus']
        _vals = [h['mon_updated'],
                 h['mon_updated'],
                 h['mon_svcname'],
                 h['mon_nodname'],
                 h['mon_overallstatus'],
                 h['mon_ipstatus'],
                 h['mon_fsstatus'],
                 h['mon_diskstatus'],
                 h['mon_containerstatus'],
                 h['mon_appstatus'],
                 h['mon_syncstatus']]
        generic_insert('svcmon_log', _vars, _vals)
        db(db.svcmon_log.id==last[0].id).update(mon_end=h['mon_updated'])
    else:
        db(db.svcmon_log.id==last[0].id).update(mon_end=h['mon_updated'])

