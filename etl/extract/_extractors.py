from bs4 import BeautifulSoup
from requests import get

from common.util import get_path
from common.lw import get_logger, get_root_logger
from zipfile import ZipFile
from io import BytesIO
import re, os


class EventExtractor(object):

    def __init__(self, url='http://phoenixdata.org/data', base='https://s3.amazonaws.com/oeda/data/current/'):
        """
        Download all Event files from Project Phoenix

        :param url: Link to Phoenix data
        :param base: Pattern to search for links
        """

        self.url = url
        self.base = base
        self.file_links = []

        self.data_path = get_path(__file__) + '/../data/{0}'
        self.logger = get_logger(__name__)

    def _get_files(self):
        """
        Get links to files on S3 from Phoenix home page

        """

        page = get(self.url)
        soup = BeautifulSoup(page.content, 'html.parser')

        links = soup.find_all(href=re.compile(self.base))
        for link in links:
            self.file_links.append(link.contents[0])

    def extract(self):
        """
        Downloads files

        """

        self._get_files()

        for link in self.file_links:
            file_name = link.replace(self.base, '').replace('.zip', '')
            file_path = self.data_path.format(file_name)

            # skip file if it's been downloaded already
            if os.path.exists(file_path):
                continue

            self.logger.info('Downloading {0}'.format(file_name))
            r = get(link)

            # unzip file to data directory
            z = ZipFile(BytesIO(r.content))
            z.extractall(self.data_path.format('.'))

if __name__ == '__main__':

    lg = get_root_logger(filename='log.log')

    ex = EventExtractor()
    ex.extract()
    print('test')
