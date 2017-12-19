import re
import os
import sys
from . import utils
import progressbar
from mechanicalsoup import Browser


class KaggleDataDownloader:
    def __init__(self, username, password, competition_name):
        """
        
        :param username: string
            Your kaggle username
        :param password: string
            Your kaggle password
        :param competition_name: string
            The name of the competition which can be found
            in the competition url.
            For example wih this competition: 
                https://www.kaggle.com/c/planet-understanding-the-amazon-from-space
            The competition name would be: planet-understanding-the-amazon-from-space
        """
        self.username = username
        self.password = password
        self.competition_name = competition_name

    def download_dataset(self, dataset_name, destination_path):
        """
        
        :param dataset_name: string
            The name of the dataset you want to download
        :param destination_path: string
            The path where you want to store the dataset
        :return: string
            The path where the dataset was downloaded
        """
        try:
            browser = self._login()
            base = 'https://www.kaggle.com'
            data_url = '/'.join([base, 'c', self.competition_name, 'data'])
            data_page = browser.get(data_url)

            data = str(data_page.soup)
            links = re.findall(
                '"url":"(/c/{}/download/[^"]+)"'.format(self.competition_name), data
            )
            for link in links:
                url = base + link
                if dataset_name is None or url.endswith('/' + dataset_name):
                    return self._download_file(browser, url, destination_path)

        except Exception as e:
            print(e, file=sys.stderr)

    @staticmethod
    def decompress(file_path, destination_path):
        """
            Uncompress an archive
        :param file_path: string
            Path of your dataset archive
        :param destination_path: string
            Path where you want to extract your file
        """
        file_type = utils.get_archive_type(file_path)
        if file_type == '7z':
            utils.extract_7_zip(file_path, destination_path)
        elif file_type == 'zip':
            utils.extract_zip(file_path, destination_path)
        elif file_type == 'tar':
            utils.extract_tar(file_path, destination_path)

    def _download_file(self, browser, url, destination_path):
        local_filename = url.split('/')[-1]
        headers = {}
        done = False
        file_size = 0
        content_length = int(
            browser.request('head', url).headers.get('Content-Length')
        )

        widgets = [local_filename, ' ', progressbar.Percentage(), ' ',
                   progressbar.Bar(marker='#'), ' ',
                   progressbar.ETA(), ' ', progressbar.FileTransferSpeed()]

        local_filename = destination_path + local_filename
        print('downloading {} to {}\n'.format(url, local_filename))
        if os.path.isfile(local_filename):
            file_size = os.path.getsize(local_filename)
            if file_size < content_length:
                headers['Range'] = 'bytes={}-'.format(file_size)
            else:
                done = True

        finished_bytes = file_size

        if file_size == content_length:
            print('{} already downloaded !'.format(local_filename))
            return local_filename
        elif file_size > content_length:
            raise Exception('Something wrong here, Incorrect file !')
        else:
            bar = progressbar.ProgressBar(widgets=widgets,
                                          maxval=content_length).start()
            bar.update(finished_bytes)

        if not done:
            stream = browser.get(url, stream=True, headers=headers)
            if not self.is_downloadable(stream):
                warning = (
                    'Warning:'
                    'download url for file {} resolves to an html document'
                    'rather than a downloadable file. \n'
                    'See the downloaded file for details.'
                    'Is it possible you have not'
                    'accepted the competition\'s rules on the kaggle website?'.format(local_filename)
                )
                raise Exception('{}\n'.format(warning))
            os.makedirs(os.path.dirname(local_filename), exist_ok=True)
            with open(local_filename, 'ab') as f:
                for chunk in stream.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        finished_bytes += len(chunk)
                        bar.update(finished_bytes)
            bar.finish()
        return local_filename

    def is_downloadable(self, response):
        '''
        Checks whether the response object is a html page
        or a likely downloadable file.
        Intended to detect error pages or prompts
        such as kaggle's competition rules acceptance prompt.
        Returns True if the response is a html page. False otherwise.
        '''

        content_type = response.headers.get('Content-Type', '')
        content_disp = response.headers.get('Content-Disposition', '')

        if 'text/html' in content_type and 'attachment' not in content_disp:
            # This response is a html file
            # which is not marked as an attachment,
            # so we likely hit a rules acceptance prompt
            return False
        return True

    def _login(self):
        login_url = 'https://www.kaggle.com/account/login'
        browser = Browser()

        login_page = browser.get(login_url)
        token = re.search('antiForgeryToken: \'(?P<token>.+)\'', str(login_page.soup)).group(1)
        login_result_page = browser.post(login_url,
                                         data={
                                             'username': self.username,
                                             'password': self.password,
                                             '__RequestVerificationToken': token
                                         })

        error_match = re.search('"errors":\["(?P<error>.+)"\]', str(login_result_page.soup))
        if error_match:
            raise Exception('There was an error logging in: ' + error_match.group(1))

        return browser
