# -*- coding: utf-8 -*-
import tweepy
import pandas as pd
import argparse

from myutils.ToolsBase import ToolsBase

class FollowingsAndFollowerScraperCommandLineArgs():
    def __init__(self) -> None:
        try:
            parser = argparse.ArgumentParser(description='FollowingsAndFollowerScraper.')
            parser.add_argument(
                '-c',
                '--config',
                default=FollowingsAndFollowerScraper.ConfFile,
                help='config json file path. (default is FollowingsAndFollowerScraper.json)'
            )

            args = parser.parse_args()
            self.config = args.config
        except Exception as ex:
            message = f"コマンドライン引数の取得に失敗したため、強制終了します。{ex}"
            ToolsBase(FollowingsAndFollowerScraper.ConfFile).logger.critical(message)


class FollowingsAndFollowerScraper(ToolsBase):
    ConfFile = "FollowingsAndFollowerScraper.json"

    def __init__(self, args: FollowingsAndFollowerScraperCommandLineArgs) -> None:
        super().__init__(args.config)
        CK = self.config["TWITTER"]["CONSUMER_KEY"]
        CS = self.config["TWITTER"]["CONSUMER_SEC_KEY"]
        AT = self.config["TWITTER"]["ACCESS_TOKEN"]
        AS = self.config["TWITTER"]["ACCESS_SEC_TOKEN"]

        auth = tweepy.OAuthHandler(CK, CS)
        auth.set_access_token(AT, AS)
        self.api = tweepy.API(auth, wait_on_rate_limit=True)

        cols = ['id', 'name', 'screen_name']

        self.followers_ids = pd.DataFrame([], columns=cols)
        self.followings_ids = pd.DataFrame([], columns=cols)

    def _main(self):
        self._scrape_all()
        self._output()

        return self

    def _scrape_all(self):
        self._scrape_followers()
        self._scrape_followings()

        return self

    def _scrape_followers(self):
        self.followers_ids = self._scrape(self.api.followers_ids, self.followers_ids)

        return self

    def _scrape_followings(self):
        self.followings_ids = self._scrape(self.api.friends_ids, self.followings_ids)

        return self

    def _scrape(self, ids, data_frame):
        for following_id in tweepy.Cursor(ids, id=self.config["TWITTER"]["ID"], cursor=-1).items():
            user = self.api.get_user(following_id)
            record = pd.Series([following_id, user.name, user.screen_name], index=data_frame.columns)
            data_frame = data_frame.append(record, ignore_index=True)

        return data_frame.append(record, ignore_index=True)


    def _output(self):
        self.followers_ids.to_csv(self.config["OUTPUT"]["FOLLOWERS"])
        self.followings_ids.to_csv(self.config["OUTPUT"]["FOLLOWINGS"])

        return self

if __name__ == "__main__":
    FollowingsAndFollowerScraper(FollowingsAndFollowerScraperCommandLineArgs()).main()
