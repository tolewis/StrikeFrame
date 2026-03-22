from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / 'prompts'

PROMPT_BY_CHANNEL = {
    'x': 'vision-review-x.txt',
    'twitter': 'vision-review-x.txt',
    'generic': 'vision-review-generic.txt',
    'linkedin': 'vision-review-generic.txt',
    'paid-social': 'vision-review-paid-social.txt',
    'paid_social': 'vision-review-paid-social.txt',
    'paid': 'vision-review-paid-social.txt',
}


def load_prompt(channel: str = 'generic') -> str:
    key = (channel or 'generic').strip().lower()
    filename = PROMPT_BY_CHANNEL.get(key, 'vision-review-generic.txt')
    return (PROMPTS_DIR / filename).read_text().strip()
