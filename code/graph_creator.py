from statistics import median

import argparse
import seaborn as sns
import matplotlib.pyplot as plt
import json

sns.set(font_scale=1.5)
sns.set_style("whitegrid")

"""
    Graph creator - Creates graphs 
"""


class CreateGraph:
    def __init__(self, function):
        self.function = function

    def process(self):
        if self.function == "graph_fraud_channels_by_social_media_pie_chart":
            self.graph_fraud_channels_by_social_media_pie_chart()
        elif self.function == "create_account_creation_cdf":
            self.create_account_creation_cdf()
        elif self.function == "followers_metrics":
            self.followers_metrics()
        elif self.function == "posts_metrics":
            self.posts_metrics()

    def posts_metrics(self):
        with open("data/graph/graph_data/posts_data_creation.json", "r") as f_read:
            data = json.load(f_read)

        gfg = sns.ecdfplot(data)
        gfg.set(xlabel='Posts', ylabel='Count')
        save_path = "data/graph/graph_pic/posts_graph.png"
        plt.savefig(save_path, bbox_inches="tight")

        _all = data['X'] + data['Instagram'] + data['YouTube'] + data['Telegram'] + data['Facebook']
        print("Twitter median:{}".format(median(data['X'])))
        print("Instagram median:{}".format(median(data['Instagram'])))
        print("YouTube median:{}".format(median(data['YouTube'])))
        print("Telegram median:{}".format(median(data['Telegram'])))
        print("Facebook median:{}".format(median(data['Facebook'])))
        print("All median:{}".format(median(_all)))

    def followers_metrics(self):
        with open("data/graph/graph_data/follower_data.json", "r") as f_read:
            data = json.load(f_read)

        gfg = sns.ecdfplot(data)
        gfg.set(xlabel='Followers', ylabel='Count')
        plt.xscale('log')
        save_path = "data/graph/graph_pic/followers_graph.png"
        plt.savefig(save_path, bbox_inches="tight")
        #
        print("Twitter median:{}".format(median(data['X'])))
        print("Instagram median:{}".format(median(data['Instagram'])))
        print("YouTube median:{}".format(median(data['YouTube'])))
        print("Telegram median:{}".format(median(data['Telegram'])))
        print("Facebook median:{}".format(median(data['Facebook'])))

        _all = data['X'] + data['Instagram'] + data['YouTube'] + data['Telegram'] + data['Facebook']

        print("All median:{}".format(median(_all)))

        print("Twitter zero input:{}".format(data['X'].count(0)))
        print("Instagram zero input:{}".format(data['Instagram'].count(0)))
        print("YouTube zero input:{}".format(data['YouTube'].count(0)))
        print("Telegram zero input:{}".format(data['Telegram'].count(0)))
        print("Facebook zero input:{}".format(data['Telegram'].count(0)))

    def create_account_creation_cdf(self):
        with open("data/graph/graph_data/new_account_creation_data_updated.json", "r") as f_read:
            data = json.load(f_read)

        gfg = sns.ecdfplot(data)
        gfg.set(xlabel='Date of Creation', ylabel='Count')
        gfg.set_xticklabels(gfg.get_xticklabels(), rotation=30)

        save_path = "data/graph/graph_pic/account_create_date.png"
        plt.savefig(save_path)

        print("Twitter median:{}".format(median(data['X'])))
        print("Instagram median:{}".format(median(data['Instagram'])))
        print("YouTube median:{}".format(median(data['YouTube'])))
        print("Telegram median:{}".format(median(data['Telegram'])))
        print("Facebook median:{}".format(median(data['Facebook'])))

        _all = data['X'] + data['Instagram'] + data['YouTube'] + data['Telegram'] + data['Facebook']
        print("All median:{}".format(median(_all)))

    def graph_fraud_channels_by_social_media_pie_chart(self):
        save_path = "data/graph/graph_pic/graph_fraud_channels_by_social_media_pie_chart.png"

        data = [147 + 12 + 34, 8 + 63 + 41, 47 + 28 + 268, 1 + 28, 23 + 32 + 757]
        labels = ['Facebook', 'Telegram', 'YouTube', 'Instagram', 'X']
        palette_color = sns.color_palette('deep')
        plt.pie(x=data, labels=labels, colors=None, autopct='%.0f%%')
        plt.savefig(save_path, bbox_inches="tight")


if __name__ == "__main__":
    _arg_parser = argparse.ArgumentParser(description="Graph creator")
    _arg_parser.add_argument("-f", "--function",
                             action="store",
                             required=True,
                             help="processing function name")

    _arg_value = _arg_parser.parse_args()

    Graph_ = CreateGraph(_arg_value.function)
    Graph_.process()
