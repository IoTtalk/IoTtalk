
class DataPath():
    def __init__(self):
        self.na_id = None

        self.idf_mac_addr = ''
        self.idf_d_name = ''
        self.idf_df_name = ''       # device feature name  ex: G-sensor
        self.idf_dfo_id = None      # dfo_id of IDF
        self.idf_type = []          # ['sample', 'sample', 'sample']
        self.idf_norm = False       # enable dynamic range or not
        self.idf_range = []         # min_max [(-20, 20), (-20, 20), (-20, 20)]
        self.idf_fn_id = None       # 1
        self.idf_fn_name = ''
        self.idf_fn = None          # f1.run, None means disable

        self.join_enable = False    # True/False
        self.join_params = []         # [(idf_mac_addr, idf_df_name, na_id), ...] | None
        self.join_fn_id = None      # 6
        self.join_fn_name = ''
        self.join_fn = None         # f6.run

        self.odf_mac_addr = ''
        self.odf_d_name = ''
        self.odf_df_name = ''
        self.odf_dfo_id = None      # dfo_id of ODF
        self.odf_scaling = False    # enable dynamic range or not
        self.odf_range = []         # min_max [(0,4), ...]
        self.odf_fn_id = []         # [2, 1, ...]
        self.odf_fn_name = []
        self.odf_fn = []            # [f2.run, f1.run, ...]

    def __str__(self):
        return (
            'DataPath( na_id={0.na_id}\n'
            '--IDF(dfo_id={0.idf_dfo_id}({0.idf_mac_addr}, {0.idf_df_name}), idf_type={0.idf_type}, norm={0.idf_norm}, fn_name={0.idf_fn_name})\n'
            '--JOIN(enable={0.join_enable}, params={0.join_params}, fn_name="{0.join_fn_name}")\n'
            '--ODF(dfo_id={0.odf_dfo_id}({0.odf_mac_addr}, {0.odf_df_name}), scaling={0.odf_scaling}, fn_name={0.odf_fn_name})\n'
            ')'
        ).format(self)
