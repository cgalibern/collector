nodes_cols = [
    'assetname',
    'fqdn',
    'serial',
    'model',
    'environnement',
    'role',
    'status',
    'type',
    'sec_zone',
    'loc_country',
    'loc_zip',
    'loc_city',
    'loc_addr',
    'loc_building',
    'loc_floor',
    'loc_room',
    'loc_rack',
    'enclosure',
    'enclosureslot',
    'hvvdc',
    'hvpool',
    'hv',
    'os_name',
    'os_release',
    'os_vendor',
    'os_arch',
    'os_kernel',
    'cpu_dies',
    'cpu_cores',
    'cpu_threads',
    'cpu_model',
    'cpu_freq',
    'mem_banks',
    'mem_slots',
    'mem_bytes',
    'listener_port',
    'version',
    'action_type',
    'host_mode',
    'team_responsible',
    'team_integ',
    'team_support',
    'project',
    'last_boot',
    'power_supply_nb',
    'power_cabinet1',
    'power_cabinet2',
    'power_protect',
    'power_protect_breaker',
    'power_breaker1',
    'power_breaker2',
    'warranty_end',
    'maintenance_end',
    'os_obs_warn_date',
    'os_obs_alert_date',
    'hw_obs_warn_date',
    'hw_obs_alert_date',
    'updated',
]

nodes_colprops = {
    'id': HtmlTableColumn(
             title = 'Id',
             field='id',
             display = False,
             img = 'columns',
             table = 'nodes',
            ),
    'node_updated': HtmlTableColumn(
             title = 'Last node update',
             field='node_updated',
             display = False,
             img = 'time16',
             table = 'nodes',
             _class = 'datetime_daily',
            ),
    'updated': HtmlTableColumn(
             title = 'Last node update',
             field='updated',
             display = False,
             img = 'time16',
             table = 'nodes',
             _class = 'datetime_daily',
            ),
    'loc_country': HtmlTableColumn(
             title = 'Country',
             field='loc_country',
             display = False,
             img = 'loc',
             table = 'nodes',
            ),
    'loc_zip': HtmlTableColumn(
             title = 'ZIP',
             field='loc_zip',
             display = False,
             img = 'loc',
             table = 'nodes',
            ),
    'loc_city': HtmlTableColumn(
             title = 'City',
             field='loc_city',
             display = False,
             img = 'loc',
             table = 'nodes',
            ),
    'loc_addr': HtmlTableColumn(
             title = 'Address',
             field='loc_addr',
             display = False,
             img = 'loc',
             table = 'nodes',
            ),
    'loc_building': HtmlTableColumn(
             title = 'Building',
             field='loc_building',
             display = False,
             img = 'loc',
             table = 'nodes',
            ),
    'loc_floor': HtmlTableColumn(
             title = 'Floor',
             field='loc_floor',
             display = False,
             img = 'loc',
             table = 'nodes',
            ),
    'loc_room': HtmlTableColumn(
             title = 'Room',
             field='loc_room',
             display = False,
             img = 'loc',
             table = 'nodes',
            ),
    'loc_rack': HtmlTableColumn(
             title = 'Rack',
             field='loc_rack',
             display = False,
             img = 'loc',
             table = 'nodes',
            ),
    'os_concat': HtmlTableColumn(
             title = 'OS full name',
             field='os_concat',
             display = False,
             img = 'os16',
             table = 'nodes',
            ),
    'os_name': HtmlTableColumn(
             title = 'OS name',
             field='os_name',
             display = False,
             img = 'os16',
             table = 'nodes',
             _class = 'os_name',
            ),
    'os_release': HtmlTableColumn(
             title = 'OS release',
             field='os_release',
             display = False,
             img = 'os16',
             table = 'nodes',
            ),
    'os_vendor': HtmlTableColumn(
             title = 'OS vendor',
             field='os_vendor',
             display = False,
             img = 'os16',
             table = 'nodes',
            ),
    'os_arch': HtmlTableColumn(
             title = 'OS arch',
             field='os_arch',
             display = False,
             img = 'os16',
             table = 'nodes',
            ),
    'os_kernel': HtmlTableColumn(
             title = 'OS kernel',
             field='os_kernel',
             display = False,
             img = 'os16',
             table = 'nodes',
            ),
    'cpu_vendor': HtmlTableColumn(
             title = 'CPU vendor',
             field='cpu_vendor',
             display = False,
             img = 'cpu16',
             table = 'nodes',
            ),
    'cpu_dies': HtmlTableColumn(
             title = 'CPU dies',
             field='cpu_dies',
             display = False,
             img = 'cpu16',
             table = 'nodes',
            ),
    'cpu_cores': HtmlTableColumn(
             title = 'CPU cores',
             field='cpu_cores',
             display = False,
             img = 'cpu16',
             table = 'nodes',
            ),
    'last_boot': HtmlTableColumn(
             title = 'Last boot',
             field='last_boot',
             display = False,
             img = 'time16',
             table = 'nodes',
            ),
    'sec_zone': HtmlTableColumn(
             title = 'Security zone',
             field='sec_zone',
             display = False,
             img = 'fw16',
             table = 'nodes',
            ),
    'cpu_threads': HtmlTableColumn(
             title = 'CPU threads',
             field='cpu_threads',
             display = False,
             img = 'cpu16',
             table = 'nodes',
            ),
    'cpu_model': HtmlTableColumn(
             title = 'CPU model',
             field='cpu_model',
             display = False,
             img = 'cpu16',
             table = 'nodes',
            ),
    'cpu_freq': HtmlTableColumn(
             title = 'CPU freq',
             field='cpu_freq',
             display = False,
             img = 'cpu16',
             table = 'nodes',
            ),
    'mem_banks': HtmlTableColumn(
             title = 'Memory banks',
             field='mem_banks',
             display = False,
             img = 'mem16',
             table = 'nodes',
            ),
    'mem_slots': HtmlTableColumn(
             title = 'Memory slots',
             field='mem_slots',
             display = False,
             img = 'mem16',
             table = 'nodes',
            ),
    'mem_bytes': HtmlTableColumn(
             title = 'Memory',
             field='mem_bytes',
             display = False,
             img = 'mem16',
             table = 'nodes',
            ),
    'nodename': HtmlTableColumn(
             title = 'Node name',
             field='nodename',
             display = False,
             img = 'node16',
             table = 'nodes',
             _class="nodename",
            ),
    'version': HtmlTableColumn(
             title = 'Agent version',
             field='version',
             display = False,
             img = 'svc',
             table = 'nodes',
            ),
    'action_type': HtmlTableColumn(
             title = 'Action type',
             field='action_type',
             display = False,
             img = 'svc',
             table = 'nodes',
            ),
    'listener_port': HtmlTableColumn(
             title = 'Listener port',
             field='listener_port',
             display = False,
             img = 'svc',
             table = 'nodes',
            ),
    'assetname': HtmlTableColumn(
             title = 'Asset name',
             field='assetname',
             display = False,
             img = 'node16',
             table = 'nodes',
            ),
    'fqdn': HtmlTableColumn(
             title = 'Fqdn',
             field='fqdn',
             display = False,
             img = 'node16',
             table = 'nodes',
            ),
    'hvvdc': HtmlTableColumn(
             title = 'Virtual datacenter',
             field='hvvdc',
             display = False,
             img = 'hv16',
             table = 'nodes',
            ),
    'hvpool': HtmlTableColumn(
             title = 'Hypervisor pool',
             field='hvpool',
             display = False,
             img = 'hv16',
             table = 'nodes',
            ),
    'hv': HtmlTableColumn(
             title = 'Hypervisor',
             field='hv',
             display = False,
             img = 'hv16',
             table = 'nodes',
            ),
    'enclosure': HtmlTableColumn(
             title = 'Enclosure',
             field='enclosure',
             display = False,
             img = 'loc',
             table = 'nodes',
            ),
    'enclosureslot': HtmlTableColumn(
             title = 'Enclosure Slot',
             field='enclosureslot',
             display = False,
             img = 'loc',
             table = 'nodes',
            ),
    'serial': HtmlTableColumn(
             title = 'Serial',
             field='serial',
             display = False,
             img = 'node16',
             table = 'nodes',
            ),
    'model': HtmlTableColumn(
             title = 'Model',
             field='model',
             display = False,
             img = 'node16',
             table = 'nodes',
            ),
    'team_responsible': HtmlTableColumn(
             title = 'Team responsible',
             field='team_responsible',
             display = False,
             img = 'guys16',
             table = 'nodes',
             _class = 'groups',
            ),
    'team_integ': HtmlTableColumn(
             title = 'Integrator',
             field='team_integ',
             display = False,
             img = 'guys16',
             table = 'nodes',
             _class = 'groups',
            ),
    'team_support': HtmlTableColumn(
             title = 'Support',
             field='team_support',
             display = False,
             img = 'guys16',
             table = 'nodes',
             _class = 'groups',
            ),
    'project': HtmlTableColumn(
             title = 'Project',
             field='project',
             display = False,
             img = 'svc',
             table = 'nodes',
            ),
    'role': HtmlTableColumn(
             title = 'Role',
             field='role',
             display = False,
             img = 'node16',
             table = 'nodes',
            ),
    'host_mode': HtmlTableColumn(
             title = 'Host Mode',
             field='host_mode',
             display = False,
             img = 'svc',
             table = 'nodes',
             _class = 'env',
            ),
    'environnement': HtmlTableColumn(
             title = 'Env',
             field='environnement',
             display = False,
             img = 'node16',
             table = 'nodes',
             _class = 'env',
            ),
    'warranty_end': HtmlTableColumn(
             title = 'Warranty end',
             field='warranty_end',
             display = False,
             img = 'time16',
             table = 'nodes',
             _class = 'date_future',
            ),
    'os_obs_warn_date': HtmlTableColumn(
             title = 'OS obsolescence warning date',
             field='os_obs_warn_date',
             display = False,
             img = 'time16',
             table = 'nodes',
             _class = 'date_future',
            ),
    'os_obs_alert_date': HtmlTableColumn(
             title = 'OS obsolescence alert date',
             field='os_obs_alert_date',
             display = False,
             img = 'time16',
             table = 'nodes',
             _class = 'date_future',
            ),
    'hw_obs_warn_date': HtmlTableColumn(
             title = 'Hardware obsolescence warning date',
             field='hw_obs_warn_date',
             display = False,
             img = 'time16',
             table = 'nodes',
             _class = 'date_future',
            ),
    'hw_obs_alert_date': HtmlTableColumn(
             title = 'Hardware obsolescence alert date',
             field='hw_obs_alert_date',
             display = False,
             img = 'time16',
             table = 'nodes',
             _class = 'date_future',
            ),
    'maintenance_end': HtmlTableColumn(
             title = 'Maintenance end',
             field='maintenance_end',
             display = False,
             img = 'time16',
             table = 'nodes',
             _class = 'date_future',
            ),
    'status': HtmlTableColumn(
             title = 'Status',
             field='status',
             display = False,
             img = 'node16',
             table = 'nodes',
            ),
    'type': HtmlTableColumn(
             title = 'Type',
             field='type',
             display = False,
             img = 'node16',
             table = 'nodes',
            ),
    'power_supply_nb': HtmlTableColumn(
             title = 'Power supply number',
             field='power_supply_nb',
             display = False,
             img = 'pwr',
             table = 'nodes',
            ),
    'power_cabinet1': HtmlTableColumn(
             title = 'Power cabinet #1',
             field='power_cabinet1',
             display = False,
             img = 'pwr',
             table = 'nodes',
            ),
    'power_cabinet2': HtmlTableColumn(
             title = 'Power cabinet #2',
             field='power_cabinet2',
             display = False,
             img = 'pwr',
             table = 'nodes',
            ),
    'power_protect': HtmlTableColumn(
             title = 'Power protector',
             field='power_protect',
             display = False,
             img = 'pwr',
             table = 'nodes',
            ),
    'power_protect_breaker': HtmlTableColumn(
             title = 'Power protector breaker',
             field='power_protect_breaker',
             display = False,
             img = 'pwr',
             table = 'nodes',
            ),
    'power_breaker1': HtmlTableColumn(
             title = 'Power breaker #1',
             field='power_breaker1',
             display = False,
             img = 'pwr',
             table = 'nodes',
            ),
    'power_breaker2': HtmlTableColumn(
             title = 'Power breaker #2',
             field='power_breaker2',
             display = False,
             img = 'pwr',
             table = 'nodes',
            ),
}

node_hba_colprops = {
    'nodename': HtmlTableColumn(
             title='Nodename',
             table='node_hba',
             field='nodename',
             img='hw16',
             display=True,
             _class="nodename",
            ),
    'hba_id': HtmlTableColumn(
             title='Hba id',
             table='node_hba',
             field='hba_id',
             img='hd16',
             display=True,
            ),
    'hba_type': HtmlTableColumn(
             title='Hba type',
             table='node_hba',
             field='hba_type',
             img='hd16',
             display=True,
            ),
    'disk_updated': HtmlTableColumn(
             title='Updated',
             table='node_hba',
             field='updated',
             img='time16',
             display=True,
             _class="datetime_daily",
            ),
}


