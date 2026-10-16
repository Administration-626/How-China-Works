# -*- coding: utf-8 -*-
"""从 EPUB 抽取正文纯文本 + 插图（含原书图注）base64 数据。"""
import zipfile, re, html, io, json, os
from PIL import Image

SRC = r'D:\MyFileSystem\000-Inbox-中转站\020-Download-下载\置身事内：中国政府与经济发展 (兰小欢) (z-library.sk, 1lib.sk, z-lib.sk).epub'
OUT = os.path.dirname(os.path.abspath(__file__))
z = zipfile.ZipFile(SRC)

# 章节文件 -> (id, 标题, 分组, 展示名)
CH = [
    ('part0005.xhtml', 'pre',    '前言 从了解现状开始', 'front'),
    ('part0007.xhtml', '1.0',    '第一章 地方政府的权力与事务', 'p1'),
    ('part0008.xhtml', '1.1',    '第一节 政府治理的特点', 'p1'),
    ('part0009.xhtml', '1.2',    '第二节 外部性与规模经济', 'p1'),
    ('part0010.xhtml', '1.3',    '第三节 复杂信息', 'p1'),
    ('part0011.xhtml', '1.4',    '第四节 激励相容', 'p1'),
    ('part0012.xhtml', '1.5',    '第五节 招商引资', 'p1'),
    ('part0013.xhtml', '1.6',    '第一章 结语', 'p1'),
    ('part0014.xhtml', '1.7',    '第一章 扩展阅读', 'p1'),
    ('part0015.xhtml', '2.0',    '第二章 财税与政府行为', 'p2'),
    ('part0016.xhtml', '2.1',    '第一节 分税制改革', 'p2'),
    ('part0017.xhtml', '2.2',    '第二节 土地财政', 'p2'),
    ('part0018.xhtml', '2.3',    '第三节 纵向不平衡与横向不平衡', 'p2'),
    ('part0019.xhtml', '2.4',    '第二章 结语', 'p2'),
    ('part0020.xhtml', '2.5',    '第二章 扩展阅读', 'p2'),
    ('part0021.xhtml', '3.0',    '第三章 政府投融资与债务', 'p3'),
    ('part0022.xhtml', '3.1',    '第一节 城投公司与土地金融', 'p3'),
    ('part0023.xhtml', '3.2',    '第二节 地方政府债务', 'p3'),
    ('part0024.xhtml', '3.3',    '第三节 招商引资中的地方官员', 'p3'),
    ('part0025.xhtml', '3.4',    '第三章 结语', 'p3'),
    ('part0026.xhtml', '3.5',    '第三章 扩展阅读', 'p3'),
    ('part0027.xhtml', '4.0',    '第四章 工业化中的政府角色', 'p4'),
    ('part0028.xhtml', '4.1',    '第一节 京东方与政府投资', 'p4'),
    ('part0029.xhtml', '4.2',    '第二节 光伏发展与政府补贴', 'p4'),
    ('part0030.xhtml', '4.3',    '第三节 政府产业引导基金', 'p4'),
    ('part0031.xhtml', '4.4',    '第四章 结语', 'p4'),
    ('part0032.xhtml', '4.5',    '第四章 扩展阅读', 'p4'),
    ('part0034.xhtml', '5.0',    '第五章 城市化与不平衡', 'p5'),
    ('part0035.xhtml', '5.1',    '第一节 房价与居民债务', 'p5'),
    ('part0036.xhtml', '5.2',    '第二节 不平衡与要素市场改革', 'p5'),
    ('part0037.xhtml', '5.3',    '第三节 经济发展与贫富差距', 'p5'),
    ('part0038.xhtml', '5.4',    '第五章 结语', 'p5'),
    ('part0039.xhtml', '5.5',    '第五章 扩展阅读', 'p5'),
    ('part0040.xhtml', '6.0',    '第六章 债务与风险', 'p6'),
    ('part0041.xhtml', '6.1',    '第一节 债务与经济衰退', 'p6'),
    ('part0042.xhtml', '6.2',    '第二节 债台为何高筑：欧美的教训', 'p6'),
    ('part0043.xhtml', '6.3',    '第三节 中国的债务与风险', 'p6'),
    ('part0044.xhtml', '6.4',    '第四节 化解债务风险', 'p6'),
    ('part0045.xhtml', '6.5',    '第六章 结语', 'p6'),
    ('part0046.xhtml', '6.6',    '第六章 扩展阅读', 'p6'),
    ('part0047.xhtml', '7.0',    '第七章 国内国际失衡', 'p7'),
    ('part0048.xhtml', '7.1',    '第一节 低消费与产能过剩', 'p7'),
    ('part0049.xhtml', '7.2',    '第二节 中美贸易冲突', 'p7'),
    ('part0050.xhtml', '7.3',    '第三节 再平衡与国内大循环', 'p7'),
    ('part0051.xhtml', '7.4',    '第七章 结语', 'p7'),
    ('part0052.xhtml', '7.5',    '第七章 扩展阅读', 'p7'),
    ('part0053.xhtml', '8.0',    '第八章 总结：政府与经济发展', 'p8'),
    ('part0054.xhtml', '8.1',    '第一节 地区间竞争', 'p8'),
    ('part0055.xhtml', '8.2',    '第二节 政府的发展与转型', 'p8'),
    ('part0056.xhtml', '8.3',    '第三节 发展目标与发展过程', 'p8'),
    ('part0057.xhtml', '8.4',    '第八章 结语', 'p8'),
    ('part0058.xhtml', '8.5',    '第八章 扩展阅读', 'p8'),
    ('part0059.xhtml', 'end',    '结束语', 'end'),
]

# 章标题（章级单页 part0007 等）的展示
CHAPTER_TITLE = {
    '1.0': '第一章 地方政府的权力与事务', '2.0': '第二章 财税与政府行为',
    '3.0': '第三章 政府投融资与债务', '4.0': '第四章 工业化中的政府角色',
    '5.0': '第五章 城市化与不平衡', '6.0': '第六章 债务与风险',
    '7.0': '第七章 国内国际失衡', '8.0': '第八章 总结：政府与经济发展',
}


def clean_lines(raw):
    """把 xhtml 转成行列表，处理竖排拆字。"""
    r = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', raw, flags=re.S | re.I)
    r = re.sub(r'<a [^>]*></a>', '', r)
    r = re.sub(r'<img[^>]*>', '\n[[IMG]]\n', r)
    lines = [l.strip() for l in re.sub(r'<[^>]+>', '\n', html.unescape(r)).split('\n')]
    lines = [l for l in lines if l]
    out, buf = [], []
    for l in lines:
        if l == '[[IMG]]':
            if buf:
                out.append(''.join(buf)); buf = []
            out.append('[[IMG]]'); continue
        if len(l) == 1:
            buf.append(l); continue
        if buf:
            out.append(''.join(buf)); buf = []
        out.append(l)
    if buf:
        out.append(''.join(buf))
    return out


chapters = []
fig_list = []
fig_meta = {}       # imgname -> {caption, note, src}
fi = 0

for fn, cid, title, grp in CH:
    raw = z.read('OEBPS/Text/' + fn).decode('utf-8', 'ignore')
    lines = clean_lines(raw)

    # 每个 img 的原书图注：同 div.chatu_img 内 p.tuti / p.tuzhu
    blocks = re.findall(r'<div class="chatu_img">(.*?)</div>', raw, re.S)
    blk_iter = []
    for b in blocks:
        imgs = re.findall(r'<img[^>]*src="([^"]+)"', b)
        tuti = re.findall(r'<p class="tuti">(.*?)</p>', b, re.S)
        tuzhu = re.findall(r'<p class="tuzhu">(.*?)</p>', b, re.S)
        for k, im in enumerate(imgs):
            blk_iter.append((im.split('/')[-1], {
                'caption': re.sub(r'\s+', '', html.unescape(re.sub(r'<[^>]+>', '', tuti[0]))) if tuti else '',
                'note': ' '.join(re.sub(r'\s+', '', html.unescape(re.sub(r'<[^>]+>', '', t))) for t in tuzhu),
            }))
    cap_map = dict(blk_iter)

    body = []
    k = 0
    for l in lines:
        if l == '[[IMG]]':
            body.append({'t': 'IMG', 'i': k}); k += 1
        else:
            body.append({'t': 'P', 'x': l})

    for n in range(k):
        # 找到该 img 在 raw 中第 n 次出现对应的文件名
        pass

    # 按 raw 中出现顺序取 img 名
    names = [m.group(1).split('/')[-1] for m in re.finditer(r'<img[^>]*src="([^"]+)"', raw)]
    for n, nm in enumerate(names):
        meta = cap_map.get(nm, {'caption': '', 'note': ''})
        fig_list.append({'id': 'f%02d' % fi, 'img': nm, 'ch': cid, **meta})
        fig_meta[nm] = 'f%02d' % fi
        fi += 1

    chapters.append({'id': cid, 'title': title, 'group': grp, 'body': body,
                     'nimg': len(names)})

# ---- 原书未标图号的正文插图，补人工说明（均为正文原话的标签化，非新增论断） ----
CAP_PATCH = {
    'image00191': ('消费、收入与储蓄的关系式', '正文原话：居民消费等于收入减去储蓄。'),
}
for f in fig_list:
    if f['img'] in CAP_PATCH and not f['caption']:
        f['caption'], f['note'] = CAP_PATCH[f['img']]

# ---- 图片压缩 ----
THUMB_W, MID_W = 320, 860
figs_db = {}
for f in fig_list:
    b = z.read('OEBPS/Images/%s' % f['img'])
    im = Image.open(io.BytesIO(b)).convert('RGB')
    w, h = im.size

    def enc(target_w, q):
        t = im if w <= target_w else im.resize((target_w, max(1, round(h * target_w / w))), Image.LANCZOS)
        buf = io.BytesIO()
        t.save(buf, 'WEBP', quality=q, method=6)
        return 'data:image/webp;base64,' + __import__('base64').b64encode(buf.getvalue()).decode()

    figs_db[f['id']] = {'big': enc(MID_W, 72), 'th': enc(THUMB_W, 55),
                        'w': w, 'h': h, 'caption': f['caption'], 'note': f['note'],
                        'ch': f['ch'], 'img': f['img']}

json.dump({'chapters': chapters, 'figs': figs_db, 'order': [f['id'] for f in fig_list]},
          open(os.path.join(OUT, 'book.json'), 'w', encoding='utf-8'), ensure_ascii=False)

tot = sum(len(v['big']) + len(v['th']) for v in figs_db.values())
print('章节:', len(chapters), '图片:', len(figs_db), 'base64 总字符:', tot, '≈', round(tot / 1024 / 1024, 2), 'MB')
for f in fig_list:
    print(f['id'], f['ch'], '|', f['caption'][:60])
