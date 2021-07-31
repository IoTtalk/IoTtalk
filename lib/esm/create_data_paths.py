# Although it doesn't work here.
__ALL__ = ['create_data_paths']

from types import FunctionType
import logging

from sqlalchemy import asc, desc, or_

import db
import ec_config
db.connect(ec_config.DB_NAME)

try:
    from . import data_path
except:
    # for test
    import data_path

DF_FUNC_DIR_NAME = 'df_func'

MAPPING_FUNC_FREFIX = '''\
from esm.{}.helper_func import \
    read_data, write_data, csmapi, \
    json_loads, json_dumps
'''.format(DF_FUNC_DIR_NAME)

esmBuiltInVariable = ''

FORBIDDEN_IMPORT = '''\
raise ImportError('Forbidden to import.')
'''


def load_df_func(session, fn_id, u_id, lock=None):
    fnvs = ( # get user-modified version "and" global version.
        session.query(db.FunctionVersion)
        .filter(db.FunctionVersion.fn_id == fn_id)
        .filter(db.FunctionVersion.completeness == True)
        .filter(or_(
            db.FunctionVersion.u_id == u_id,
            db.FunctionVersion.u_id == None,
        ))
        .order_by(desc(db.FunctionVersion.date))
        .all()
    )
    # MySQL can use nullslast() to get the user-modified version first, but
    # SQLite cannot. So get this by hand.
    fnv = sorted(fnvs, key=lambda x: 1 if x.u_id is None else 0)[0]

    if not fnv:
        # no version exists.(maybe the function is not complete yet.)
        raise Exception('The DF function is not complete: ' + str(fn_id))

    fn_name = (session.query(db.Function.fn_name) 
               .select_from(db.Function)
               .filter(db.Function.fn_id == fn_id)
               .first())
    if fn_name: fn_name  = fn_name[0]
    else: fn_name = fn_id

    ### if 'import' in fnv.code:
    ###     FORBIDDEN_IMPORT needs to be implemented

    if fnv.is_switch:
        code = fnv.non_df_args + '\n' + fnv.code
    else:
        code = fnv.code

    context = {}
    try:
        code_object = compile(MAPPING_FUNC_FREFIX + esmBuiltInVariable  +code, fn_name, 'exec')
        exec(code_object, context)
    except Exception as e:
        raise Exception('User function "'+ fn_name +'" compilation error: ' + str(e))

    fn = context.get('run', None)
    if fn is None:
        raise Exception('"run" function is not found in user function "' + fn_name + '"')
    elif not isinstance(fn, FunctionType):
        raise Exception('"run" must be a function in user function "' + fn_name + '"')

    return fn


def get_fn_name(session, idf_fn_id):
    if not idf_fn_id: return False
    fn = (
        session.query(db.Function)
        .filter(db.Function.fn_id == idf_fn_id)
        .first()
    )
    if not (fn and fn.fn_name): return False
    return fn.fn_name


def get_alias_from_df_name(db, session, mac_addr, df_name):  #From a specific device object, not from the default DeviceFeature table.
    try:
        alias_name = (session.query(db.DFObject.alias_name)
                .select_from(db.DFObject)
                .join(db.DeviceObject)
                .join(db.Device)
                .join(db.DeviceModel)
                .join(db.DM_DF)
                .join(db.DeviceFeature)
                .filter(db.DFObject.do_id == db.DeviceObject.do_id)
                .filter(db.Device.mac_addr == mac_addr)
                .filter(db.Device.d_id == db.DeviceObject.d_id)
                .filter(db.DeviceObject.dm_id == db.DeviceModel.dm_id)
                .filter(db.DeviceModel.dm_id == db.DM_DF.dm_id)
                .filter(db.DM_DF.df_id == db.DeviceFeature.df_id)
                .filter(db.DeviceFeature.df_id == db.DFObject.df_id)
                .filter(db.DeviceFeature.df_name == df_name)
                .all()
               )
        alias_name = [a[0] for a in alias_name]
    except Exception:
        return None
    else:
        return alias_name


def create_data_paths(session, p_id, u_id, lock=None):
    global esmBuiltInVariable
    log = logging.getLogger(__name__)

    all_data_paths = []
    log.info('{LC}' + '='*10 + 'create_data_paths' + '='*10)

    unbound_ODF_objs = (
        session.query(
            db.DFObject.dfo_id,)
           .select_from(db.DFObject)
           .join(db.DeviceObject)
           .join(db.Project)
           .join(db.DeviceFeature)
           .filter(db.Project.p_id == p_id)
           .filter(db.DeviceFeature.df_type == 'output')
           .filter(db.DeviceObject.d_id == None)
    )
    unbound_odfObject_ID = []
    for obj in unbound_ODF_objs:
        unbound_odfObject_ID.append(obj.dfo_id)

    query_nas = (
        session.query(db.NetworkApplication)
        .filter(db.NetworkApplication.p_id == p_id)
    )
    for na in query_nas:
        na_id = na.na_id

        # get join_* (part 1/2): join_enable, join_params
        # NOTE: the device object may not bound by any device.
        query_join_params = (
            session.query(
                db.Device.mac_addr,
                db.DeviceFeature.df_name,
            )
            .select_from(db.MultipleJoin_Module)
            .join(
                (db.DFObject,
                 db.MultipleJoin_Module.dfo_id == db.DFObject.dfo_id
                ),
                (db.DeviceFeature,
                 db.DFObject.df_id == db.DeviceFeature.df_id
                ),
                (db.DeviceObject,
                 db.DFObject.do_id == db.DeviceObject.do_id
                ),
                (db.Device,
                 db.DeviceObject.d_id == db.Device.d_id
                ),
            )
            .filter(db.MultipleJoin_Module.na_id == na_id)
            .order_by(asc(db.MultipleJoin_Module.param_i))
            .all()
        )

        if not query_join_params:
            join_enable = False
            join_params = []
            join_fn_id = None
            join_fn_name = ''
            join_fn = None
        else:
            join_enable = True
            join_params = []
            for mac_addr, df_name in query_join_params:
                join_params.append((mac_addr, df_name, na_id))

            # get join_* (part 2/2): join_fn_id, join_fn_name, join_fn
            query_join_fn = (
                session.query(db.Function)
                .select_from(db.MultipleJoin_Module)
                .join(
                    (db.Function,
                     db.MultipleJoin_Module.fn_id == \
                     db.Function.fn_id
                    ),
                )
                .filter(db.MultipleJoin_Module.na_id == na_id)
                .first()
            )
            if query_join_fn:
                join_fn_id = query_join_fn.fn_id
                join_fn_name = query_join_fn.fn_name

                join_fn = load_df_func(session, join_fn_id, u_id, lock)
 
            else:
                join_fn_id = None
                join_fn_name = 'disabled'
                join_fn = None

        log.info('{LC}NA(na_id=%s, join_enable=%s, join_fn_name="%s")',
                 na_id, join_enable, join_fn_name)


        # get idf_* (part 1/2):
        #   idf_mac_addr, idf_d_name, idf_df_name, idf_dfo_id, idf_norm
        query_idfs = (
            session.query(
                db.Device.mac_addr,
                db.Device.d_name,
                db.DeviceFeature.df_name,
                db.DFObject.dfo_id,
                db.DF_Module.normalization,
            )
            .select_from(db.DFObject)
            .join(
                (db.DeviceObject,
                 db.DFObject.do_id == db.DeviceObject.do_id
                ),
                (db.DeviceFeature,
                 db.DFObject.df_id == db.DeviceFeature.df_id
                ),
                (db.Device,
                 db.DeviceObject.d_id == db.Device.d_id
                ),
                (db.DF_Module,
                 db.DFObject.dfo_id == db.DF_Module.dfo_id
                ),
            )
            .filter(
                db.DF_Module.na_id == na_id,
                db.DeviceFeature.df_type == 'input',
            )
            .group_by(db.DF_Module.dfo_id)
            .all()
        )

        for (idf_mac_addr, idf_d_name, idf_df_name, idf_dfo_id,
                idf_norm) in query_idfs:
            log.info('{LC}    IDF(%s, %s)', idf_d_name, idf_df_name)

            idf_alias = idf_df_name
            alias = get_alias_from_df_name(db, session, idf_mac_addr, idf_df_name)
            if alias: idf_alias = alias[0]
            esmBuiltInVariable = 'idf_alias_="{}"\nidf_df_name_="{}"\nidf_d_name_="{}"\nidf_mac_addr_="{}"\n'.format(idf_alias, idf_df_name, idf_d_name, idf_mac_addr)

            # get idf_* (part 2/2): idf_type, idf_range
            query_idf_params = (
                session.query(
                    db.DF_Module.idf_type,
                    db.DF_Module.min,
                    db.DF_Module.max,
                )
                .filter(db.DF_Module.dfo_id == idf_dfo_id)
                .filter(db.DF_Module.na_id == na_id)
                .order_by(asc(db.DF_Module.param_i))
                .all()
            )
            idf_type = []
            idf_range = []
            for (idf_type_field,
                 minimum, maximum) in query_idf_params:
                idf_type.append(idf_type_field)
                idf_range.append((minimum, maximum))


            # get odf_* (part 1/2):
            #   odf_mac_addr, odf_d_name, odf_df_name, odf_dfo_id, odf_scaling
            query_odfs = (
                session.query(
                    db.DeviceFeature.df_name,
                    db.DFObject.dfo_id,
                    db.DF_Module.normalization,)
                .select_from(db.DFObject)
                .join(
                    (db.DeviceObject,
                     db.DFObject.do_id == db.DeviceObject.do_id
                    ),
                    (db.DeviceFeature,
                     db.DFObject.df_id == db.DeviceFeature.df_id
                    ),
                    (db.DF_Module,
                     db.DFObject.dfo_id == db.DF_Module.dfo_id
                    ),
                )
                .filter(
                    db.DF_Module.na_id == na_id,
                    db.DeviceFeature.df_type == 'output',
                )
                .group_by(db.DF_Module.dfo_id)
                .all()
            )

            for (odf_df_name, odf_dfo_id, odf_scaling) in query_odfs:
                odf_mac_addr = None
                odf_d_name  = None
                if odf_dfo_id not in unbound_odfObject_ID: 
                    query_device_info = (session.query(
                        db.Device.mac_addr,
                        db.Device.d_name,)
                    .select_from(db.Device)                 
                    .join(db.DeviceObject)
                    .join(db.DFObject)
                    .filter(db.DFObject.dfo_id == odf_dfo_id)
                    .first())
                    if query_device_info:
                        odf_mac_addr = query_device_info.mac_addr
                        odf_d_name = query_device_info.d_name

                log.info('{LC}        ODF(%s, %s)', odf_d_name, odf_df_name)

                # get odf_* (part 2/2):
                #   odf_range, odf_fn_id, odf_fn_name, odf_fn
                query_odf_params = (
                    session.query(
                        db.DF_Module.min,
                        db.DF_Module.max,
                    )
                    .filter(db.DF_Module.dfo_id == odf_dfo_id)
                    .filter(db.DF_Module.na_id == na_id)
                    .order_by(asc(db.DF_Module.param_i))
                    .all()
                )
                odf_range = []
                odf_scaling_flag = False

                odf_alias = odf_df_name
                alias = get_alias_from_df_name(db, session, odf_mac_addr, odf_df_name)
                if alias: odf_alias = alias[0]
                esmBuiltInVariable = esmBuiltInVariable + 'odf_alias_="{}"\nodf_df_name_="{}"\nodf_d_name_="{}"\nodf_mac_addr_="{}"\n'.format(odf_alias, odf_df_name, odf_d_name, odf_mac_addr)

                for (minimum, maximum) in query_odf_params:
                    odf_range.append((minimum, maximum))
                    odf_scaling_flag = (minimum != maximum) or odf_scaling_flag

                # create DataPath instance.
                path = data_path.DataPath()
                path.na_id = na_id
                path.idf_mac_addr = idf_mac_addr
                path.idf_d_name = idf_d_name
                path.idf_df_name = idf_df_name
                path.idf_dfo_id = idf_dfo_id
                path.idf_type = idf_type
                path.idf_norm = idf_norm
                path.idf_range = idf_range
                path.join_enable = join_enable
                path.join_params = join_params
                path.join_fn_id = join_fn_id
                path.join_fn_name = join_fn_name
                path.join_fn = join_fn
                path.odf_mac_addr = odf_mac_addr
                path.odf_d_name = odf_d_name
                path.odf_df_name = odf_df_name
                path.odf_dfo_id = odf_dfo_id
                path.odf_scaling = odf_scaling_flag
                path.odf_range = odf_range
                all_data_paths.append(path)
            # end of query_odfs
        # end of query_idfs
        log.info('')
    # end of query_nas

    for path in all_data_paths:
        log.info('{LC}%s', path)
        log.info('')
    log.info('{LC}' + '='*10 + 'create_data_paths' + '='*10)

    return all_data_paths


def test():
    import db
    import ec_config
    db.connect(ec_config.DB_NAME)

    import clogging
    clogging.basicConfig(level=logging.DEBUG)

    session = db.get_session()
    create_data_paths(session, 1, 1)


if __name__ == '__main__':
    test()

# vim:se colorcolumn=70:
