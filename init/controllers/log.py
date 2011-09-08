img_h = {
  'networks': 'net16.png',
  'dns': 'dns16.png',
  'service': 'svc.png',
  'apps': 'svc.png',
  'auth': 'guys16.png',
  'users': 'guys16.png',
  'group': 'guys16.png',
  'user': 'guy16.png',
  'ack': 'check16.png',
  'compliance': 'check16.png',
  'moduleset': 'action16.png',
  'module': 'action16.png',
  'action': 'action16.png',
  'filterset': 'filter16.png',
  'filter': 'filter16.png',
  'add': 'add16.png',
  'delete': 'del16.png',
  'change': 'rename16.png',
  'rename': 'rename16.png',
  'attach': 'attach16.png',
  'detach': 'detach16.png',
}

class col_log_evt(HtmlTableColumn):
    def get(self, o):
        try:
            d = json.loads(o.log_dict)
            for k in d:
                if not isinstance(d[k], str):
                    d[k] = str(d[k])
                d[k] = d[k].encode('utf8')
            s = T.translate(o.log_fmt,d)
        except KeyError:
            s = 'error parsing: %s'%o.log_dict
        except json.decoder.JSONDecodeError:
            s = 'error loading JSON: %s'%o.log_dict
        except UnicodeEncodeError:
            s = 'error transcoding: %s'%o.log_dict
        except TypeError:
            s = 'type error: %s'%o.log_dict
        return s

class col_log_icons(HtmlTableColumn):
    def get(self, o):
        return o.log_action

    def html(self, o):
        t = self.get(o)
        l = t.split('.')
        i = []
        d = []
        for w in l:
            if w not in img_h or img_h[w] in d:
                continue
            d.append(img_h[w])
            i.append(IMG( _src=URL(r=request,c='static',f=img_h[w])))
        return SPAN(i)

class col_log_level(HtmlTableColumn):
    def html(self, o):
       d = self.get(o)
       if d == "info":
           return DIV(d, _class="boxed_small bggreen")
       elif d == "warning":
           return DIV(d, _class="boxed_small bgorange")
       elif d == "error":
           return DIV(d, _class="boxed_small bgred")
       else:
           return DIV(d, _class="boxed_small bgblack")

class table_log(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['log_date',
                     'log_icons',
                     'log_level',
                     'log_svcname',
                     'log_nodename',
                     'log_user',
                     'log_action',
                     'log_evt',
                     'log_fmt',
                     'log_dict',
                     'log_entry_id',
                     'log_gtalk_sent',
                     'log_email_sent']
        self.colprops = {
            'log_date': HtmlTableColumn(
                     title='Date',
                     field='log_date',
                     img='time16',
                     display=True,
                    ),
            'log_icons': col_log_icons(
                     title='Icons',
                     field='log_icons',
                     img='action16',
                     display=True,
                    ),
            'log_level': col_log_level(
                     title='Icons',
                     field='log_level',
                     img='action16',
                     display=True,
                    ),
            'log_action': HtmlTableColumn(
                     title='Action',
                     field='log_action',
                     img='action16',
                     display=True,
                    ),
            'log_svcname': HtmlTableColumn(
                     title='Service',
                     field='log_svcname',
                     img='svc',
                     display=True,
                    ),
            'log_nodename': HtmlTableColumn(
                     title='Node',
                     field='log_nodename',
                     img='node16',
                     display=True,
                    ),
            'log_user': HtmlTableColumn(
                     title='User',
                     field='log_user',
                     img='guy16',
                     display=True,
                    ),
            'log_evt': col_log_evt(
                     title='Event',
                     field='dummy',
                     img='log16',
                     display=True,
                    ),
            'log_fmt': HtmlTableColumn(
                     title='Format',
                     field='log_fmt',
                     img='log16',
                     display=False,
                    ),
            'log_dict': HtmlTableColumn(
                     title='Dictionary',
                     field='log_dict',
                     img='log16',
                     display=False,
                    ),
            'log_entry_id': HtmlTableColumn(
                     title='Entry id',
                     field='log_entry_id',
                     img='log16',
                     display=False,
                    ),
            'log_gtalk_sent': HtmlTableColumn(
                     title='Sent via gtalk',
                     field='log_gtalk_sent',
                     img='log16',
                     display=False,
                    ),
            'log_email_sent': HtmlTableColumn(
                     title='Sent via email',
                     field='log_email_sent',
                     img='log16',
                     display=False,
                    ),
        }
        self.dbfilterable = False
        self.ajax_col_values = 'ajax_log_col_values'
        self.special_filtered_cols = ['log_icons', 'log_evt']

@auth.requires_login()
def ajax_log_col_values():
    t = table_log('log', 'ajax_log')
    col = request.args[0]
    o = db.log[col]
    q = db.log.id > 0
    for f in set(t.cols)-set(t.special_filtered_cols):
        q = _where(q, 'log', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_log():
    t = table_log('log', 'ajax_log')
    o = ~db.log.log_date
    q = db.log.id > 0
    for f in set(t.cols)-set(t.special_filtered_cols):
        q = _where(q, 'log', t.filter_parse(f), f)
    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)

    return t.html()

@auth.requires_login()
def log():
    t = DIV(
          ajax_log(),
          _id='log',
        )
    return dict(table=t)


