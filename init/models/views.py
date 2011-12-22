def user_name():
    if not hasattr(session.auth, 'user'):
        return 'Unknown'
    return ' '.join([session.auth.user.first_name,
                     session.auth.user.last_name])

def _where(query, table, var, field):
    if query is None:
        query = (db[table].id > 0)
    if var is None: return query
    if len(var) == 0: return query

    if '&' in var and '|' in var:
        """don't even try to guess order
        """
        return query

    done = False

    if var[0] == '|':
        _or=True
        var = var[1:]
    elif var[0] == '&':
        _or=False
        var = var[1:]
    else:
        _or=False

    if '&' in var:
        i = var.index('&')
        chunk = var[:i]
        var = var[i:]
    elif '|' in var:
        i = var.index('|')
        chunk = var[:i]
        var = var[i:]
    else:
        done = True
        chunk = var

    if len(chunk) == 0:
        return query

    if chunk[0] == '!':
        _not = True
        chunk = chunk[1:]
    else:
        _not = False

    if len(chunk) == 0:
        return query

    # initialize a restrictive filter
    q = db[table].id < 0

    if chunk == 'empty':
        q = (db[table][field]==None)|(db[table][field]=='')
    elif chunk[0] not in '<>=':
        if field not in db[table]:
            pass
        elif db[table][field].type == 'string':
            if '%' in chunk:
                q = db[table][field].like(chunk)
            else:
                q = db[table][field]==chunk
        elif db[table][field].type in ('id', 'integer'):
            try:
               c = int(chunk)
               q = db[table][field]==c
            except:
               pass
        elif db[table][field].type in ('float'):
            try:
               c = float(chunk)
               q = db[table][field]==c
            except:
               pass
    else:
        _op = chunk[0]

        if len(chunk) == 0:
            return query

        chunk = chunk[1:]
        if _op == '>':
            q = db[table][field]>chunk
        elif _op == '<':
            q = db[table][field]<chunk
        elif _op == '=':
            q = db[table][field]==chunk

    if _not:
        q = ~q

    if not done:
        q = _where(q, table, var, field)

    if _or:
        return query|q
    else:
        return query&q

def domainname(fqdn):
    if fqdn is None or fqdn == "":
        return
    l = fqdn.split('.')
    if len(l) < 2:
        return
    l[0] = ""
    return '.'.join(l)

def user_fset_id():
    q = db.gen_filterset_user.user_id == auth.user_id
    row = db(q).select(db.gen_filterset_user.fset_id).first()
    if row is None:
        return 0
    return row.fset_id

def user_fset_name():
    q = db.gen_filterset_user.user_id == auth.user_id
    q &= db.gen_filterset_user.fset_id == db.gen_filtersets.id
    row = db(q).select(db.gen_filtersets.fset_name).first()
    if row is None:
        return 0
    return row.gen_filtersets.fset_name

def or_apply_filters(q, node_field=None, service_field=None, fset_id=None):
    if fset_id is None:
        v = db.v_gen_filtersets
        o = v.f_order
        qry = db.gen_filterset_user.fset_id == v.fset_id
        qry &= db.gen_filterset_user.user_id == auth.user_id
    else:
        qry = db.v_gen_filtersets.fset_id == fset_id

    rows = db(qry).select()
    if len(rows) == 0:
        if node_field is not None:
            q |= node_field.like("%")
        if service_field is not None:
            q |= service_field.like("%")
        return q

    nodes = set([])
    services = set([])
    for row in rows:
        nodes, services = filterset_query(row, nodes, services)

    n_nodes = len(nodes)
    n_services = len(services)

    if n_nodes > 0 and n_services > 0 and node_field is not None and service_field is not None:
        q |= (node_field.belongs(nodes)) | (service_field.belongs(services))
    elif len(nodes) > 0 and node_field is not None:
        q |= node_field.belongs(nodes)
    elif len(services) > 0 and service_field is not None:
        q |= service_field.belongs(services)

    return q

def apply_filters(q, node_field=None, service_field=None, fset_id=None):
    if fset_id is None:
        v = db.v_gen_filtersets
        o = v.f_order
        qry = db.gen_filterset_user.fset_id == v.fset_id
        qry &= db.gen_filterset_user.user_id == auth.user_id
    else:
        qry = db.v_gen_filtersets.fset_id == fset_id

    rows = db(qry).select()
    if len(rows) == 0:
        return q

    nodes = set([])
    services = set([])
    for row in rows:
        nodes, services = filterset_query(row, nodes, services)

    n_nodes = len(nodes)
    n_services = len(services)

    if n_nodes > 0 and n_services > 0 and node_field is not None and service_field is not None:
        q &= (node_field.belongs(nodes)) | (service_field.belongs(services))
    elif len(nodes) > 0 and node_field is not None:
        q &= node_field.belongs(nodes)
    elif len(services) > 0 and service_field is not None:
        q &= service_field.belongs(services)

    return q

def filterset_query(row, nodes, services):
    if 'v_gen_filtersets' in row:
        v = row.v_gen_filtersets
    else:
        v = row

    if v.encap_fset_id > 0:
        o = db.v_gen_filtersets.f_order
        qr = db.v_gen_filtersets.fset_id == v.encap_fset_id
        rows = db(qr).select(orderby=o)
        for r in rows:
            nodes, services = filterset_query(r, nodes, services)
    elif v.f_table is None or v.f_field is None:
        return nodes, services

    else:
        if v.f_op == '=':
            qry = db[v.f_table][v.f_field] == v.f_value
        elif v.f_op == '!=':
            qry = db[v.f_table][v.f_field] != v.f_value
        elif v.f_op == 'LIKE':
            qry = db[v.f_table][v.f_field].like(v.f_value)
        elif v.f_op == 'NOT LIKE':
            qry = ~db[v.f_table][v.f_field].like(v.f_value)
        elif v.f_op == 'IN':
            qry = db[v.f_table][v.f_field].belongs(v.f_value.split(','))
        elif v.f_op == 'NOT IN':
            qry = ~db[v.f_table][v.f_field].belongs(v.f_value.split(','))
        elif v.f_op == '>=':
            qry = db[v.f_table][v.f_field] >= v.f_value
        elif v.f_op == '>':
            qry = db[v.f_table][v.f_field] > v.f_value
        elif v.f_op == '<=':
            qry = db[v.f_table][v.f_field] <= v.f_value
        elif v.f_op == '<':
            qry = db[v.f_table][v.f_field] < v.f_value
        else:
            return nodes, services

        if "NOT" in v.f_log_op:
            qry = ~qry

        if v.f_table == 'services':
            rows = db(qry).select(db.services.svc_name,
                                  groupby=db.services.svc_name)
            n_nodes = set([])
            n_services = set(map(lambda x: x.svc_name, rows))
        elif v.f_table == 'nodes':
            rows = db(qry).select(db.nodes.nodename,
                                  groupby=db.nodes.nodename)
            n_nodes = set(map(lambda x: x.nodename, rows))
            n_services = set([])
        elif v.f_table == 'svcmon':
            rows = db(qry).select(db.svcmon.mon_nodname,
                                  db.svcmon.mon_svcname,
                                  groupby=db.svcmon.mon_nodname)
            n_nodes = set(map(lambda x: x.mon_nodname, rows))
            n_services = set(map(lambda x: x.mon_svcname, rows))
        else:
            raise Exception(str(v))

        if 'AND' in v.f_log_op:
            if v.f_table == 'nodes' or v.f_table == 'svcmon':
                if nodes == set([]):
                    nodes = n_nodes
                else:
                    nodes &= n_nodes
            elif v.f_table == 'services' or v.f_table == 'svcmon':
                if services == set([]):
                    services = n_services
                else:
                    services &= n_services
        elif 'OR' in v.f_log_op:
            if v.f_table == 'nodes' or v.f_table == 'svcmon':
                if nodes == set([]):
                    nodes = n_nodes
                else:
                    nodes |= n_nodes
            elif v.f_table == 'services' or v.f_table == 'svcmon':
                if services == set([]):
                    services = n_services
                else:
                    services |= n_services

    return nodes, services

def apply_gen_filters(q, tables=[]):
    v = db.v_gen_filtersets
    o = v.f_order
    qry = db.gen_filterset_user.fset_id == v.fset_id
    qry &= db.gen_filterset_user.user_id == auth.user_id
    rows = db(qry).select()
    for row in rows:
        q = gen_filterset_query(q, row, tables)
    return q

joins = {
  'svcmon':{
    'svcmon': None,
    'dashboard': (db.svcmon.mon_svcname == db.dashboard.dash_svcname) & \
                 (db.svcmon.mon_nodname == db.dashboard.dash_nodename),
    'v_svcmon': None,
    'checks_live': (db.svcmon.mon_svcname == db.checks_live.chk_svcname) & \
                   (db.svcmon.mon_nodname == db.checks_live.chk_nodename),
    'comp_log': (db.svcmon.mon_svcname == db.comp_log.run_svcname) & \
                (db.svcmon.mon_nodname == db.comp_log.run_nodename),
    'comp_status': (db.svcmon.mon_svcname == db.comp_status.run_svcname) & \
                   (db.svcmon.mon_nodname == db.comp_status.run_nodename),
    'svcmon_log': (db.svcmon.mon_svcname == db.svcmon_log.mon_svcname) & \
                  (db.svcmon.mon_nodname == db.svcmon_log.mon_nodname),
    'services_log': db.svcmon.mon_svcname == db.services_log.svc_name,
    'svcmon_log': (db.svcmon.mon_svcname == db.svcmon_log.mon_svcname) & \
                  (db.svcmon.mon_nodname == db.svcmon_log.mon_nodname),
  },
  'services':{
    'services': None,
    'dashboard': db.services.svc_name == db.dashboard.dash_svcname,
    'v_svcmon': None,
    'checks_live': db.services.svc_name == db.checks_live.chk_svcname,
    'appinfo': db.services.svc_name == db.appinfo.app_svcname,
    'comp_log': db.services.svc_name == db.comp_log.run_svcname,
    'comp_status': db.services.svc_name == db.comp_status.run_svcname,
    'svcmon_log': db.services.svc_name == db.svcmon_log.mon_svcname,
    'services_log': db.services.svc_name == db.services_log.svc_name,
    'v_apps': db.services.svc_app == db.apps.app,
  },
  'nodes':{
    'nodes': None,
    'v_nodes': None,
    'dashboard': db.nodes.nodename == db.dashboard.dash_nodename,
    'dashboard': db.nodes.nodename == db.dashboard.dash_nodename,
    'v_svcmon': None,
    'v_nodes': None,
    'v_svcactions': None,
    'checks_live': db.nodes.nodename == db.checks_live.chk_nodename,
    'packages': db.nodes.nodename == db.packages.pkg_nodename,
    'patches': db.nodes.nodename == db.patches.patch_nodename,
    'comp_rulesets_nodes': db.nodes.nodename == db.comp_rulesets_nodes.nodename,
    'v_comp_nodes': None,
    'comp_log': db.nodes.nodename == db.comp_log.run_nodename,
    'comp_status': db.nodes.nodename == db.comp_status.run_nodename,
    'svcmon_log': db.nodes.nodename == db.svcmon_log.mon_nodname,
    'services_log': (db.svcmon.mon_svcname == db.services_log.svc_name) & (db.svcmon.mon_nodname == db.nodes.nodename),
    'v_apps': (db.nodes.team_responsible == db.auth_group.role) & \
              (db.auth_group.id == db.apps_responsibles.group_id) & \
              (db.apps_responsibles.app_id) & (db.apps.id),
  },
}
def gen_filterset_query(q, row, tables=[]):
    if 'v_gen_filtersets' in row:
        v = row.v_gen_filtersets
    else:
        v = row

    if v.encap_fset_id > 0:
        o = db.v_gen_filtersets.f_order
        qr = db.v_gen_filtersets.fset_id == v.encap_fset_id
        rows = db(qr).select(orderby=o)
        qry = None
        for r in rows:
            qry = gen_filterset_query(qry, r, tables)
    elif v.f_table is None or v.f_field is None:
        return q
    else:
        f_table = v.f_table
        if v.f_table not in tables:
            joined = False
            for t in tables:
                if t is None:
                    continue
                try:
                    j = joins[v.f_table][t]
                    if j is None:
                        # for views, where the fields of v.f_table are
                        # available through t
                        f_table = t
                    else:
                        if q is None:
                            q = j
                        else:
                            q &= j
                        tables.add(v.f_table)
                    joined = True
                    break
                except KeyError:
                    continue
            if not joined:
                # can not apply filter
                return q
        if v.f_op == '=':
            qry = db[f_table][v.f_field] == v.f_value
        elif v.f_op == '!=':
            qry = db[f_table][v.f_field] != v.f_value
        elif v.f_op == 'LIKE':
            qry = db[f_table][v.f_field].like(v.f_value)
        elif v.f_op == 'NOT LIKE':
            qry = ~db[f_table][v.f_field].like(v.f_value)
        elif v.f_op == 'IN':
            qry = db[f_table][v.f_field].belongs(v.f_value.split(','))
        elif v.f_op == 'NOT IN':
            qry = ~db[f_table][v.f_field].belongs(v.f_value.split(','))
        elif v.f_op == '>=':
            qry = db[f_table][v.f_field] >= v.f_value
        elif v.f_op == '>':
            qry = db[f_table][v.f_field] > v.f_value
        elif v.f_op == '<=':
            qry = db[f_table][v.f_field] <= v.f_value
        elif v.f_op == '<':
            qry = db[f_table][v.f_field] < v.f_value
        else:
            return q
    if qry is None:
       return q
    if q is None:
        q = qry
    elif v.f_log_op == 'AND':
        q &= qry
    elif v.f_log_op == 'AND NOT':
        q &= ~qry
    elif v.f_log_op == 'OR':
        q |= qry
    elif v.f_log_op == 'OR NOT':
        q |= ~qry
    return q

