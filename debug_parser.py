import re

with open('data/modified_sms_v2_clean.xml', 'r', encoding='utf-8') as f:
    content = f.read()

print('File length:', len(content))
print('First 500 chars:')
print(content[:500])
print('\nLooking for SMS pattern...')
sms_pattern = r'<sms[^>]+body="([^"]+)".*?readable_date="([^"]+)"'
matches = re.findall(sms_pattern, content, re.DOTALL)
print('Found', len(matches), 'matches')
if matches:
    print('First match body:', matches[0][0][:100])
    print('First match date:', matches[0][1])