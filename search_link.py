import requests
from bs4 import BeautifulSoup
import json

class LinkedeinScrape():
    search_urls = {'now':'https://www.linkedin.com/vsearch/p?company={}&openAdvancedForm=true&companyScope=C&locationType=Y&rsid=1961852231483569446408&orig=MDYS',
                  'later':'https://www.linkedin.com/vsearch/p?company={}&openAdvancedForm=true&companyScope=P&locationType=Y&rsid=1961852231483569533727&orig=MDYS'}

    login_info_url = 'https://www.linkedin.com/uas/login'
    login_url = 'https://www.linkedin.com/uas/login-submit'
    session = None
    result_now = []
    result_later = []

    def __init__(self, company_name, login, password):
        self.company_name = company_name
        self.login = login
        self.password = password
        for key, value in self.search_urls.items():
            url = value.format(company_name)
            self.search_urls[key] = url

    def session(self):
        self.session = requests.Session()

        html = self.session.get(self.login_info_url).text
        soup = BeautifulSoup(html)
        csrf = soup.find(id="loginCsrfParam-login")['value']

        login_information = {
            'session_key': self.login,
            'session_password': self.password,
            'loginCsrfParam': csrf
        }

        self.session.post(self.login_url, data=login_information, headers=dict(referer=self.login_url))


    def scrape_search_url(self):

        for key, value in self.search_urls.items():
            for n in range(1,100 +1):
                url = self.search_urls[key] + '&page_num=%d' % (n)
                search = self.session.get(url, headers=dict(referer=url)).text
                search_html = BeautifulSoup(search, "lxml")

                code_block = search_html.find(id="voltron_srp_main-content").__str__()
                code_block = code_block.split('<!--')[1].split('-->')[0]
                print(code_block)
                data = json.loads(code_block)

                if key == 'now':
                    person_now = {}
                    search_result = data['content']['page']['voltron_unified_search_json']['search']['baseData']['resultCount']
                    person_now.update({
                        'company': self.company_name,
                        'work_in': key,
                        'search_result' : search_result
                    })
                    for person in data['content']['page']['voltron_unified_search_json']['search']['results']:
                        for _ in person.items():
                            person_now.update({
                                'id': person['person']['id'],
                                'name' : person['person']['fmt_name'],
                                'link' : person['person']['link_nprofile_view_3'],
                                'location' : person['person']['fmt_location'],
                                'industry': person['person']['fmt_industry'],
                                'field': person['person']['fmt_headline']
                            })
                        self.result_now.append(person_now)

                else:
                    person_later = {}
                    search_result = data['content']['page']['voltron_unified_search_json']['search']['baseData']['resultCount']
                    person_later.update({
                        'company': self.company_name,
                        'work_in': key,
                        'search_result': search_result
                    })
                    for person in data['content']['page']['voltron_unified_search_json']['search']['results']:
                        for _ in person.items():
                            person_later.update({
                                'id': person['person']['id'],
                                'name': person['person']['fmt_name'],
                                'link': person['person']['link_nprofile_view_3'],
                                'location': person['person']['fmt_location'],
                                'industry': person['person']['fmt_industry'],
                                'field': person['person']['fmt_headline']
                            })
                        self.result_later.append(person_later)

    def saveData(self):
        with open('now_work.json', 'w') as json_file:
            json.dump(self.result_now, json_file, indent=4)

        with open('later_work.json', 'w') as json_file:
            json.dump(self.result_later, json_file, indent=4)

    def run(self):
        self.session()
        self.scrape_search_url()
        self.saveData()


if __name__ == '__main__':
    scrape = LinkedeinScrape('enter company name', 'enter login', 'enter password')
    scrape.run()

