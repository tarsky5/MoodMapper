import pandas as pd
import snscrape.modules.twitter as sntwitter
import itertools
from textblob import Blobber, TextBlob
import re
import spacy

# Mean function

def mean(li):
    tot_sum = 0
    for i in range(0, len(li)):
        tot_sum += li[i]

    return(tot_sum / len(li))

# Functions that clean tweets to extact emotional valence

def nlp_cleaning(text):

    text = text.lower()
    text = re.sub(r'https?:\/\/\S+', '', text)
    text = re.sub(r"www\.[a-z]?\.?(com)+|[a-z]+\.(com)", '', text)
    text = re.sub(r"(@[A-Za-z0-9]+)", " ", text)
    text = text.replace('\n', ' ').replace('\r', '')
    text = ' '.join(text.split())
    text = re.sub(r"[A-Za-z\.]*[0-9]+[A-Za-z%°\.]*", "", text)
    text = re.sub(r"(\s\-\s|-$)", "", text)
    text = re.sub(r"[,\!\?\%\(\)\/\"]", "", text)
    text = re.sub(r"\&\S*\s", "", text)
    text = re.sub(r"\&", "", text)
    text = re.sub(r"\+", "", text)
    text = re.sub(r"\#", "", text)
    text = re.sub(r"\$", "", text)
    text = re.sub(r"\£", "", text)
    text = re.sub(r"\%", "", text)
    text = re.sub(r"\:", "", text)
    text = re.sub(r"\@", "", text)
    text = re.sub(r"\_", "", text)

    return(text)

def remove_emoji(string):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    
    return(emoji_pattern.sub(r'', string))


# Function that extracts the emotional valence of a given point

# Usage : getValence(lat, long, rad, n, lang) -> return float between -1 and 1.

def getValence(lat, long, rad, n, lang = "fr"):

    th_incertitude = 0.5 # Incertitude threshold
    
    if lang == "fr": #Load french stop words
        from textblob_fr import PatternTagger, PatternAnalyzer
        from spacy.lang.fr.stop_words import STOP_WORDS
        stop_words=set(STOP_WORDS)

        deselect_stop_words = ['n\'', 'ne','pas','plus','personne','aucun','ni','aucune','rien']
        for w in deselect_stop_words:
            if w in stop_words:
                stop_words.remove(w)
        
    elif lang == "en": #Use english stop words
        en = spacy.load('en_core_web_sm')
        stop_words = en.Defaults.stop_words

    # Create the string to send for the scrap
    loc = str(lat) + ", " + str(long) + ", " + str(rad) + "km"
    
    # Scrap all the geolocalised tweets in the perimeter
    df_coord = pd.DataFrame(itertools.islice(sntwitter.TwitterSearchScraper(
        'geocode:"{}"'.format(loc)).get_items(), n))[['date', 'content']]


    # Indicate the time window in wich tweets were published
    time_window = "from " + str(df_coord['date'][0]) + " to " + str(df_coord['date'][len(df_coord)-1]) + "."

    # Create the list with all the tweets contents.
    list_content = [df_coord['content'][i] for i in range(0, len(df_coord))]

    # Clean all the tweet contents
    clean_content = [remove_emoji(nlp_cleaning(list_content[i])) for i in range(0, len(list_content))]

    # List all words
    all_tweet=[]
    for tweet in clean_content:
        Word_Tok = []
        for word in re.sub("\W"," ",tweet ).split():
            Word_Tok.append(word)
        all_tweet.append(Word_Tok)

    # Remove all the stop words from the tweets
    AllfilteredTweets=[]
    for tweet in all_tweet:
        filteredTweet = [w for w in tweet if not ((w in stop_words) or (len(w) == 1))]
        AllfilteredTweets.append(' '.join(filteredTweet))

    # Load the correct analyser in function of language

    if lang == "fr":
        tb = Blobber(pos_tagger=PatternTagger(), analyzer=PatternAnalyzer())
    elif lang == "en":
        tb = TextBlob

    # Create a list with all the emotional valences
    cc_blob = [tb(AllfilteredTweets[i]).sentiment for i in range(0, len(clean_content))]

    # Filter the valences that don't have enought certitue (defined in th_incertitude)
    allValidData = []
    for tup in cc_blob:
        if tup[1] >= th_incertitude:
            allValidData.append(tup[0])

    # return mean valence of the coordonate

    return(mean(allValidData))
