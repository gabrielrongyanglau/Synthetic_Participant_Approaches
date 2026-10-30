"""Public research-funded simulation limits and configurable help text."""
import os,re

MAX_PARTICIPANTS=100
MAX_REPETITIONS=1
MAX_METHODS=1

def contact():
    email=os.environ.get('SPA_CONTACT_EMAIL','').strip()
    if re.fullmatch(r'[A-Za-z0-9.!#$%&\'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',email):
        return dict(text='Contact the research team at '+email+'.',email=email)
    return dict(text='Contact the research team through the person who shared this prototype with you.',email=None)

def estimate():
    raw=os.environ.get('SPA_ESTIMATED_MINUTES','60').strip()
    if not re.fullmatch(r'\d{1,2}(?:\s*[-–]\s*\d{1,2})?',raw) or any(not 1<=int(x)<=60 for x in re.findall(r'\d+',raw)):raw='60'
    return raw

def service_info():
    return dict(max_participants=MAX_PARTICIPANTS,max_repetitions=MAX_REPETITIONS,max_methods=MAX_METHODS,
      estimated_minutes=estimate(),estimate_note='Generation time varies. It may take a few minutes, or up to an hour when the data to be generated are more complex, for example with many variables or large pilot inputs. Service availability also affects timing. This is a planning estimate, not a guarantee.',
      funding='AI simulations currently use the research team’s API budget. If funds or service limits are reached, generation may be interrupted or temporarily unavailable.',
      future='Using your own API key and paying for your simulations is planned for a future update; it is not available yet.',contact=contact())

def check_run(req):
    if req.n!=100 or req.repetitions!=1 or len(req.methods)!=1:
        raise ValueError('This research-funded prototype permits one approach and one dataset of 100 participants per simulation. Larger datasets and repeated or multi-approach runs are currently unavailable.')

def unavailable():
    return 'The research-funded simulation service is temporarily unavailable. The team’s API budget, account limits or model access may need attention. No automatic retry was made. '+contact()['text']
