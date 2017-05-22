import re
import os
import progressbar
from mechanicalsoup import Browser
import codecs


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
            print(e)

    def unzip(self, dataset_path, destination_path):
        """
        
        :param dataset_path: string
            Path of your dataset archive
        :param destination_path: string
            Path where you want to extract your file
        """
        file_type = self._get_file_type(dataset_path)
        print("file_type", file_type)

    def _get_file_type(self, file_path):
        file_type = None
        magic_dict = {
            b"\x1f\x8b\x08": "gz",
            b"\x42\x5a\x68": "bz2",
            b"\x50\x4b\x03\x04": "zip",
            b"\x37\x7A\xBC\xAF\x27\x1C": "7z"
        }
        max_len = max(len(x) for x in magic_dict)

        with open(file_path, "rb") as f:
            file_start = f.read(max_len)
        for magic, filetype in magic_dict.items():
            if file_start.startswith(magic):
                file_type = filetype

        return file_type

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
        login_form = login_page.soup.select("#login-account")[0]
        login_form.select("#UserName")[0]['value'] = self.username
        login_form.select("#Password")[0]['value'] = self.password
        login_result = browser.submit(login_form, login_page.url)
        if login_result.url == login_url:
            error = (login_result.soup
                     .select('#standalone-signin .validation-summary-errors')[0].get_text())
            raise Exception('There was an error logging in: ' + error)

        return browser
