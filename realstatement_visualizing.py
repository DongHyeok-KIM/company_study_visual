import pandas as pd
from datetime import datetime
from matplotlib import font_manager, rc
import matplotlib.pyplot as plt
import seaborn as sns
import platform
from dateutil.relativedelta import relativedelta
from matplotlib.transforms import Bbox, TransformedBbox, blended_transform_factory
from mpl_toolkits.axes_grid1.inset_locator import BboxPatch, BboxConnector,\
    BboxConnectorPatch
from config.default_config_file import presidents_inaug_dates
from flask_restful import reqparse


class Realstatement_visualizing:
    def __init__(self):
        self.president_data = pd.DataFrame()
        self.file_name : str
        plt.rcParams['axes.unicode_minus']= False
        if platform.system() == 'Darwin': #맥os 사용자의 경우
            plt.style.use('seaborn-whitegrid')
            rc('font', family = 'AppleGothic')

    def file_name_parser(self):
        print("1")
        parser = reqparse.RequestParser()
        parser.add_argument('file_name', required=True, type=str)
        print(2, parser)
        args = parser.parse_args()
        print(3, args)
        self.file_name = str(args['file_name'])
        print(self.file_name)
        print("4")

        return self.file_name

    def load_csv_file(self, file_name):
        df = pd.read_csv('./data/'+ file_name+'.csv')
        return df

    def president_data_preprocessing(self, df):
        df['년월'] = df['년월'].apply(lambda x: datetime.strptime(x, '%Y.%m.%d'))
        df['년월'] = df['년월'].astype(str)
        df['년월'] = df['년월'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
        사용할대통령 = ['노무현', '이명박', '박근혜', '문재인']
        df = df.query('대통령이름 in @사용할대통령')
        president_data = df.reset_index(drop=True)
        return president_data


    def data_preprocessing(self, df):
        df['Unnamed: 0'] = df['Unnamed: 0'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
        df.rename(columns={"Unnamed: 0": '년월'}, inplace=True)
        president_data = self.president_data_preprocessing(self.load_csv_file('역대성향별정권'))
        df = pd.merge(president_data, df)
        df = df.melt(id_vars=df.columns[:3], value_vars=df.columns[3:],var_name='구분', value_name='값')
        df['구분'] = df['구분'].apply(lambda x: x.replace("[%]", ""))
        df['구분'] = df['구분'].apply(lambda x: x.replace("[백만원]", ""))
        df['구분'] = df['구분'].apply(lambda x: x.replace("[2019.01 = 100]", ""))

        return df

    def presidentline(self, presidents_inaug_dates, max_value):
        for president, inaug_date in presidents_inaug_dates.items():
            if president == '박근혜' or president == '문재인':
                y = 2
                m = 4
            else:
                y = 2
                m = 5
            inaug_date = datetime.strptime(inaug_date, '%Y-%m-%d')
            plt.axvline(inaug_date, linestyle='--', color='black')
            plt.text(inaug_date + relativedelta(years=y, month=m), y=max_value, s=president, fontsize=11)

    def lineplot_presidentline(self, df, name):
        print(df.head())
        temp_df = df.query('구분 == @name')
        print("lineplot_presidentline")
        print(name)
        print(temp_df)
        max_value = temp_df['값'].max() * 0.95
        sns.lineplot(data=temp_df, x='년월', y=f'값', hue='구분')
        plt.title(f'총계', fontsize=20, fontweight='bold')
        plt.legend(loc='upper left', bbox_to_anchor=(0.05, 0.9))
        self.presidentline(presidents_inaug_dates, max_value)

    def lineplot(self, df, 리스트, title):
        temp_df = df.query('구분 in @ 리스트')
        max_value = temp_df['값'].max() * 0.95
        sns.lineplot(data=temp_df, x='년월', y=f'값', hue='구분')
        plt.title(f'{title} 상세', fontsize=15, fontweight='bold')
        plt.xticks(rotation=45)

    def connect_bbox(self, bbox1, bbox2,loc1a, loc2a, loc1b, loc2b,prop_lines, prop_patches=None):
        if prop_patches is None:
            prop_patches = prop_lines.copy()
            prop_patches["alpha"] = prop_patches.get("alpha", 1) * 0.1
        c1 = BboxConnector(bbox1, bbox2, loc1=loc1a, loc2=loc2a, **prop_lines)
        c1.set_clip_on(False)
        c2 = BboxConnector(bbox1, bbox2, loc1=loc1b, loc2=loc2b, **prop_lines)
        c2.set_clip_on(False)
        bbox_patch1 = BboxPatch(bbox1, **prop_patches)
        bbox_patch2 = BboxPatch(bbox2, **prop_patches)
        p = BboxConnectorPatch(bbox1, bbox2,
                               loc1a=loc1a, loc2a=loc2a, loc1b=loc1b, loc2b=loc2b,
                               **prop_patches)
        p.set_clip_on(False)
        return c1, c2, bbox_patch1, bbox_patch2, p

    def zoom_effect02(self, ax1, ax2, **kwargs):
        tt = ax1.transScale + (ax1.transLimits + ax2.transAxes)
        trans = blended_transform_factory(ax2.transData, tt)

        mybbox1 = ax1.bbox
        mybbox2 = TransformedBbox(ax1.viewLim, trans)

        prop_patches = kwargs.copy()
        prop_patches["ec"] = "none"
        prop_patches["alpha"] = 0.2

        c1, c2, bbox_patch1, bbox_patch2, p = self.connect_bbox(mybbox1, mybbox2, loc1a=2, loc2a=3, loc1b=1, loc2b=4, prop_lines=kwargs, prop_patches=prop_patches)

        ax1.add_patch(bbox_patch1)
        ax2.add_patch(bbox_patch2)
        ax2.add_patch(c1)
        ax2.add_patch(c2)
        ax2.add_patch(p)

        return c1, c2, bbox_patch1, bbox_patch2, p



    def main_sub_choice(self, file_name):
        if file_name == '국내건설수주액':
            main = '총수주액'
            sub = ['공공부문', '민간부문']
        elif file_name =='주택매매지수':
            main = '총지수'
            sub = ['단독주택','연립주택','아파트']
        else:
            main = '전국'
            sub = ['서울', '경기', '제주']
        return main, sub

    def triple_grap(self):
        print("triple_grap", self.file_name)
        df = self.load_csv_file(self.file_name)
        print(self.file_name)
        print(df.head())
        df = self.data_preprocessing(df)
        print("전처리")
        print(df.head())

        main, sub = self.main_sub_choice(self.file_name)
        print(main, sub)
        plt.figure(figsize=(15, 10))
        ax1 = plt.subplot(2, 1, 1)
        self.lineplot_presidentline(df, main)
        ax2 = plt.subplot(2, 2, 3)
        self.lineplot(df.query(f'"2008-03-01" <= 년월 < "2013-03-01"'), sub, '이명박임기')
        self.zoom_effect02(ax2, ax1)
        ax3 = plt.subplot(2, 2, 4)
        self.lineplot(df.query(f'"2017-05-01" <= 년월'), sub, '문재인임기')
        self.zoom_effect02(ax3, ax1)
        return plt
        # plt.show()


