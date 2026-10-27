from pathlib import Path
import re
H=Path(__file__).resolve().parent;p=H/'acquisition-worked.tex'
assert not (H/'source-preservation.json').exists()
parts=re.split(r'(\$[^$]*\$)',p.read_text())
for i in range(0,len(parts),2):
    parts[i]=re.sub(r'\b(are|therefore|tax|is|goodwill|or|becomes|A|and)(?=\d)',r'\1 ',parts[i])
    parts[i]=re.sub(r',(?=\d)',', ',parts[i])
    parts[i]=parts[i].replace('}:26','}: 26').replace('source,accounting,posting','source, accounting, posting')
for i in range(1,len(parts),2):
    parts[i]='$'+parts[i][1:-1].strip()+'$'
    if parts[i-1] and parts[i-1][-1].isalnum():parts[i-1]+=' '
p.write_text(''.join(parts));print('Repaired prose-number/math boundaries before source freeze.')
