import urllib2
import re
import smtplib
import csv
import time
from bs4 import BeautifulSoup


class Craiglist():

    def __init__(self, keyword):
        self.keyword = keyword
        self.email_subject = "Regarding your add on craiglist"
        self.server = ""
        self.message = 'Subject: {}\n{}'.format(self.email_subject, self.read_email_template())
        self.cities = self.load_cities()
        self.username, self.password = self.load_auth()
        self.gmail_connect()

    def load_auth(self):
        username = password = ""
        with open('auth.txt', 'r') as file:
            for line in file:
                key, value = line.strip().split("=")
                if key == 'username':
                    username = value
                if key == 'password':
                    password = value

        if not username or not password:
            raise Exception("Error: Authentication file auth.txt is incorrect.")

        return [username, password]

    def read_email_template(self):
        data = ""
        with open('email_template.txt', 'r') as file:
            data = file.read().replace('\n', '')
        return data

    def load_cities(self):
        cities = []
        with open('cities.txt', 'r') as city:
            for line in city:
                if line.startswith('Y'):
                    cities.append(line.strip())
        return cities

    def gmail_connect(self):
        try:
            self.server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            self.server.login(self.username, self.password)
            print "Connected to gmail"
        except:
            print "Error: Something went wrong in connection"

    def send_email(self, email):
        #email = 'kalpeshtawde@outlook.com'
        message = "To: {}\n{}".format(email, self.message)
        try:
            self.server.sendmail(self.username, email, message)
            print "Email sent to {}!".format(email)
        except:
            print "Error: Something went wrong in sending email"

    def gmail_disconnect(self):
        self.server.close()

    def get_email(self, url):
        email = ""

        try:
            response = urllib2.urlopen(url)
        except Exception:
            print "Error: download failed for email url {}".format(url)
        else:
            html = response.read()

            m = re.match(".*mailto:(.*?)\?", html)
            if m:
                email = m.group(1)
                email = email.encode('utf-8')
                print "Found email {}".format(email)
            else:
                m = re.match("class=.*?mailapp.*?>(.*?)<\/a>", html)
                if m:
                    email = m.group(1)
                    email = email.encode('utf-8')

        return email

    def process(self, citylink, url):
        title = email = ""
        output = []

        try:
            response = urllib2.urlopen(url)
        except Exception:
            print "Error: download failed for url {}".format(url)
            pass
        else:
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')

            try:
                reply = soup.find(
                    'button', attrs={"class": "reply-button js-only"})['data-href']
                reply = re.sub('__SERVICE_ID__', 'contactinfo', reply)
                contact_url = "{}{}".format(citylink, reply)
                print contact_url
                email = self.get_email(contact_url)
                if email:
                    self.send_email(email)
                else:
                    print "Email did not find"
            except Exception:
                pass

            try:
                title = soup.find('span', attrs={"id":"titletextonly"}).string
                if title:
                    title = title.encode('utf-8')
            except Exception:
                pass

        return [title, email]

    def run(self):
        output_file = open('output.csv', mode='w')
        output_writer = csv.writer(output_file, delimiter=',', quotechar='"',
                                   quoting=csv.QUOTE_MINIMAL)
        output_writer.writerow(['Title', 'Email'])

        for line in self.cities:
            status, state, city, citylink = line.split("|")
            print "Processing for city {}, {}".format(city, state)
            url = ("{}/search/hhh?query={"
                        "}&sort=rel&availabilityMode=0&sale_date=all+dates").format(
                citylink, self.keyword)
            url = url.replace(" ", "+")

            response = urllib2.urlopen(url)
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')

            for link in soup.find_all('a', attrs={"class": "result-title hdrlnk"}):
                time.sleep(5)
                print "\tProcessing for link {}".format(link['href'])
                output = self.process(citylink, link['href'])
                if output:
                    output_writer.writerow(output)


if __name__ == "__main__":
    obj = Craiglist("house on rent")
    obj.run()
    obj.gmail_disconnect()
