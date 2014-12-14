import jinja2
import json
import os
import os.path
import requests
import tweepy

from bs4 import BeautifulSoup

def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s env variable" % var_name
        raise EnvironmentError(error_msg)

def get_sorted_status_links():
    print "Starting up"
    if not os.path.isfile("tweets.json"):
        print "No stored tweets"
        auth = tweepy.OAuthHandler(get_env_variable('TWITTER_KEY'), get_env_variable('TWITTER_SECRET'))
        auth.set_access_token(get_env_variable('TWITTER_TOKEN'), get_env_variable('TWITTER_TOKEN_SECRET'))

        api = tweepy.API(auth)
        api.home_timeline()
        print "Got tweets"
        statuses = [status._json for status in api.home_timeline(count=50)]
        statuses_with_links = [status for status in statuses if status['entities'] and status['entities']['urls']]

        for status in statuses_with_links:
            status['weight'] = float(status['favorite_count']) * 0.5 + float(status['retweet_count'])

        sorted_statuses = sorted(statuses_with_links, key=lambda status: status.get('weight'), reverse=True)

        with open('tweets.json', 'w') as tweets:
            json.dump(sorted_statuses, tweets)

    else:
        print "Loading tweets from file"
        with open('tweets.json') as tweets:
            json_data = tweets.read()
            sorted_statuses = json.loads(json_data)

    print "Parsing tweets"
    link_objects_to_export = []
    for status in sorted_statuses:
        link = status['entities']['urls'][0]['expanded_url']
        print "Checking %s" % (link,)
        page = requests.get(link, verify=False)
        soup = BeautifulSoup(page.text)
        link_title = soup.title.string
        link_object = [{
            'link': link,
            'link_text': link_title,
            'tweet_text': unicode(status['text']),
            'tweet_link': "https://www.twitter.com/%s/status/%s" % (status['user']['screen_name'], status['id_str']),
        }]
        link_objects_to_export += link_object

    return link_objects_to_export

def render_link_page(link_objects):
    template_loader = jinja2.FileSystemLoader('.')
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template('template.html')
    template_vars = {
        "title": "Hello",
        "links": link_objects,
    }
    print "Rendering"
    with open('index.html', 'w') as html:
        html.write(template.render(template_vars).encode('utf-8'))

if __name__ == "__main__":
    render_link_page(get_sorted_status_links())