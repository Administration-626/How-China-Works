# -*- coding: utf-8 -*-
"""四层验收：结构 / 几何 / 时序 / 引用。"""
import asyncio, json, sys, re, os, html, zipfile
from playwright.async_api import async_playwright

URL = 'http://127.0.0.1:8791/index.html'
CHROME = r'C:\Users\administer\AppData\Local\ms-playwright\chromium-1228\chrome-win64\chrome.exe'
SHOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shots')
os.makedirs(SHOT, exist_ok=True)

fail = []
def chk(ok, msg):
    print(('  OK  ' if ok else '  FAIL') + '  ' + msg)
    if not ok: fail.append(msg)


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME)
        pg = await b.new_page(viewport={'width': 1440, 'height': 940})
        errs = []
        pg.on('pageerror', lambda e: errs.append('pageerror: %s' % e))
        pg.on('console', lambda m: errs.append('console.%s: %s' % (m.type, m.text)) if m.type == 'error' else None)
        await pg.goto(URL, wait_until='load')
        await pg.wait_for_timeout(700)

        print('\n=== 第一层 · 结构断言 ===')
        st = await pg.evaluate("""() => {
          const cards=[...document.querySelectorAll('.card')];
          const ths=[...document.querySelectorAll('#figwall img')];
          return {
            cards: cards.length,
            figs: ths.length,
            thumbsLoaded: ths.filter(i=>i.naturalWidth>0).length,
            hScroll: document.documentElement.scrollWidth - document.documentElement.clientWidth,
            ranks: document.querySelectorAll('.rank-row').length,
            myths: document.querySelectorAll('.myth').length,
            tls: document.querySelectorAll('#tlwall .it').length,
            quotes: document.querySelectorAll('.qt').length,
            chips: document.querySelectorAll('.chip').length,
            loopsvg: !!document.querySelector('#loop svg'),
            afters: document.querySelectorAll('#afterwall .it').length,
            coversvg: !!document.querySelector('#cover svg'),
            verdicts: document.querySelectorAll('.vd').length,
            cmpRows: document.querySelectorAll('.cmp-row').length,
            dtabRows: document.querySelectorAll('#dt_estate .drow, #dt_fiscal .drow, #dt_macro .drow').length,
            debtRows: document.querySelectorAll('#debtbody .drow').length,
            asof: !!document.querySelector('.asof'),
            navAfter: !!document.querySelector('nav a[href="#after"]'),
            whyCards: document.querySelectorAll('.wcard').length,
            views: document.querySelectorAll('.vcard').length,
            anchors: document.querySelectorAll('#anchorwall .arow').length,
            anchorHead: document.querySelectorAll('#anchorwall .arow.hd').length,
            stances: document.querySelectorAll('.vcard .stance').length,
            navWhy: !!document.querySelector('nav a[href="#why"]') && !!document.querySelector('nav a[href="#views"]'),
            ledger: document.querySelectorAll('.lg').length,
            ledgerV: document.querySelectorAll('.lg .verdict').length,
            an: document.querySelectorAll('.an').length,
            paths: document.querySelectorAll('.pth').length,
            chains: document.querySelectorAll('.pth .chain i').length,
            aiRows: document.querySelectorAll('#vdbody .drow').length,
            navAI: !!document.querySelector('nav a[href="#ai"]') && !!document.querySelector('nav a[href="#ledger"]'),
            tracks: document.querySelectorAll('.trk').length,
            trackPairs: document.querySelectorAll('.trk .pair').length,
            trackTags: document.querySelectorAll('.trk .dtag').length,
            unknowns: document.querySelectorAll('#ukwall .uk').length,
            unote: !!document.querySelector('.unote') && !!document.querySelector('.unote .unote-b'),
            navTrack: !!document.querySelector('nav a[href="#track"]') && !!document.querySelector('nav a[href="#unknown"]'),
            nums: [...document.querySelectorAll('.sec-head .num')].map(e => e.textContent.trim()),
            navAll: document.querySelectorAll('[data-nav]').length,
            navStrip: document.querySelectorAll('#nstrip a[data-nav]').length,
            navStripG: document.querySelectorAll('#nstrip .sgrp').length,
            navPop: document.querySelectorAll('#npop a[data-nav]').length,
            navPopG: document.querySelectorAll('#npop .ph').length,
            navDots: document.querySelectorAll('#rdot a[data-nav]').length,
            navDotsG: document.querySelectorAll('#rdot a.grpstart').length,
            navMob: document.querySelectorAll('#mb a[data-nav]').length,
            navMobG: document.querySelectorAll('#mb .mh2').length,
            pbar: !!document.getElementById('pbar'),
            navIDs: [...new Set([...document.querySelectorAll('[data-nav]')].map(a => a.dataset.nav))],
            secIDs: [...document.querySelectorAll('main section[id]')].map(s => s.id),
          };
        }""")
        print(json.dumps(st, ensure_ascii=False, indent=1))
        chk(st['cards'] == 53, '章节卡片 53 张（实际 %d）' % st['cards'])
        chk(st['figs'] == 26 and st['thumbsLoaded'] == 26, '26 张缩略图全部解码（%d/%d）' % (st['thumbsLoaded'], st['figs']))
        chk(st['hScroll'] == 0, '无横向溢出（%d）' % st['hScroll'])
        chk(st['ranks'] == 16, '数量级榜 16 行')
        chk(st['myths'] == 8, '反直觉 8 条')
        chk(st['tls'] == 7, '时间轴 7 节点')
        chk(st['quotes'] == 16, '金句 16 条')
        chk(st['loopsvg'], '主线机制 SVG 存在')
        # 新增区块
        chk(st['afters'] == 8, '书成之后 8 节点（实际 %d）' % st['afters'])
        chk(st['coversvg'], '疫情掩护论时序图存在')
        chk(st['verdicts'] == 6, '判断核对 6 条（实际 %d）' % st['verdicts'])
        chk(st['cmpRows'] == 7, '原书对 2026 对照表 7 行（实际 %d）' % st['cmpRows'])
        chk(st['dtabRows'] == 25, '实况数据表 25 行（房地产10+财政5+宏观10，实际 %d）' % st['dtabRows'])
        chk(st['debtRows'] == 3, '化债进度 3 行（实际 %d）' % st['debtRows'])
        chk(st['asof'], '数据时点声明存在')
        chk(st['navAfter'], '导航含新增区块入口')
        chk(st['whyCards'] == 4, '为什么是 2020 四层动因（实际 %d）' % st['whyCards'])
        chk(st['views'] == 6, '主流说法 6 条（实际 %d）' % st['views'])
        chk(st['anchors'] == 13, '时间锚点 12 行 + 表头（实际 %d）' % st['anchors'])
        chk(st['anchorHead'] == 1, '时间锚点表头唯一（实际 %d）' % st['anchorHead'])
        chk(st['stances'] == 6, '观点立场标签 6 个（实际 %d）' % st['stances'])
        chk(st['navWhy'], '导航含为什么是2020 / 主流说法入口')
        chk(st['ledger'] == 7, '判断与追踪 7 条（实际 %d）' % st['ledger'])
        chk(st['ledgerV'] == 7, '核对条目全部带结论标签（%d/7）' % st['ledgerV'])
        chk(st['an'] == 4, 'AI 类比对照 4 组（实际 %d）' % st['an'])
        chk(st['paths'] == 3, '断裂路径 3 条（实际 %d）' % st['paths'])
        chk(st['chains'] == 14, '路径链条节点 14 个（实际 %d）' % st['chains'])
        chk(st['aiRows'] == 6, 'AI 结论分界 6 行（实际 %d）' % st['aiRows'])
        chk(st['navAI'], '导航含判断核对 / AI 类比入口')
        # 新增：当年 vs 现在 + 未知清单
        chk(st['tracks'] == 5, '当年 vs 现在 5 人（实际 %d）' % st['tracks'])
        chk(st['trackPairs'] == 10, '每人两组对照（%d/10）' % st['trackPairs'])
        chk(st['trackTags'] == 5, '每人一个追踪标签（%d/5）' % st['trackTags'])
        chk(st['unknowns'] == 4, '未知清单 4 条（实际 %d）' % st['unknowns'])
        chk(st['unote'], '推理边界提示存在')
        chk(st['navTrack'], '导航含当年 vs 现在 / 未知清单入口')
        exp_nums = ['%02d' % i for i in range(1, 20)]
        chk(st['nums'] == exp_nums,
            '章节编号 01—18 连续（实际 %s）' % ','.join(st['nums']))

        # 导航：四组、三套入口、进度条、ID 全覆盖
        print('  导航：', json.dumps({k: v for k, v in st.items() if k.startswith('nav') or k in ('pbar', 'secIDs', 'navIDs')}, ensure_ascii=False))
        chk(st['pbar'], '阅读进度条存在')
        chk(st['navStrip'] == 19, '标签条内联全部 19 项（实际 %d）' % st['navStrip'])
        chk(st['navStripG'] == 4, '标签条分 4 组（实际 %d）' % st['navStripG'])
        chk(st['navPop'] == 19, '下拉含全部 19 项（实际 %d）' % st['navPop'])
        chk(st['navPopG'] == 4, '下拉分 4 组（实际 %d）' % st['navPopG'])
        chk(st['navDots'] == 19, '右侧浮动目录 19 个点（实际 %d）' % st['navDots'])
        chk(st['navDotsG'] == 4, '浮动目录 4 组分隔（实际 %d）' % st['navDotsG'])
        chk(st['navMob'] == 19, '移动抽屉含 19 项（实际 %d）' % st['navMob'])
        chk(st['navMobG'] == 4, '移动抽屉分 4 组（实际 %d）' % st['navMobG'])
        chk(set(st['navIDs']) == set(st['secIDs']) and len(st['navIDs']) == 19,
            '导航 ID 与 19 个区块一一对应（缺 %s / 多 %s）'
            % (sorted(set(st['secIDs']) - set(st['navIDs'])), sorted(set(st['navIDs']) - set(st['secIDs']))))
        chk(st['navAll'] == 19 * 4, '三套入口加总 76 个链接（实际 %d）' % st['navAll'])

        # 可见性断言：元素在 ≠ 元素可见（曾被同名 .lb 类冲突坑过）
        vis = await pg.evaluate("""() => {
          // 只判断「有正常布局占位」，不看是否在当前视口内（长页面下方区块本就未滚动到）
          const laid = el => {
            const r = el.getBoundingClientRect();
            return r.width > 0 && r.height > 0;
          };
          const rows = [...document.querySelectorAll('.rank-row')];
          const bad = rows.filter(r => !laid(r.querySelector('.rlab'))
                        || r.querySelector('.rlab').getBoundingClientRect().width > r.getBoundingClientRect().width);
          const figs = [...document.querySelectorAll('.fig .im img')];
          const smallFigs = figs.filter(i => i.getBoundingClientRect().width < 150).length;
          const q = [...document.querySelectorAll('.qt p')];
          const badQ = q.filter(e => !laid(e)).length;
          const qOverflow = q.filter(e => e.scrollWidth > e.clientWidth + 2).length;
          return {badRows: bad.length, rows: rows.length, smallFigs: smallFigs, figs: figs.length,
                  badQ: badQ, qOverflow: qOverflow, quotes: q.length,
                  firstLabel: rows[0] ? rows[0].querySelector('.rlab').textContent : ''};
        }""")
        print('  可见性：', json.dumps(vis, ensure_ascii=False))
        chk(vis['badRows'] == 0, '数量级榜标签列正常且有占位（异常 %d）' % vis['badRows'])
        chk(vis['badQ'] == 0, '金句全部有正常布局占位（异常 %d）' % vis['badQ'])
        chk(vis['qOverflow'] == 0, '金句无横向文字溢出（%d）' % vis['qOverflow'])
        chk(vis['smallFigs'] == 0, '图表缩略图渲染尺寸正常（过小 %d/%d）' % (vis['smallFigs'], vis['figs']))
        chk('宏观债务' in vis['firstLabel'], '数量级榜首行标签文本正确（%s）' % vis['firstLabel'][:20])

        # 伪元素标签不遮挡正文：比较 ::before 右边界与正文块左边界
        ov = await pg.evaluate("""() => {
          const bad = [];
          document.querySelectorAll('.myth .q, .myth .a').forEach(el => {
            const before = getComputedStyle(el, '::before');
            // ::before 是 inline-block，正文另起一行，检查元素文本是否被压（元素高度过小则说明重叠）
            const r = el.getBoundingClientRect();
            if (r.height < 20) bad.push(el.className);
          });
          return bad;
        }""")
        chk(not ov, '反直觉卡片标签未压住正文（异常 %d）' % len(ov))

        # 对照表 / 数据表：文字不溢出、条形有占位
        addv = await pg.evaluate("""() => {
          const cellOver = [...document.querySelectorAll('.cmp-row>div, .drow .dl')]
            .filter(e => e.getBoundingClientRect().width < 40).length;
          const bars = [...document.querySelectorAll('.dbar')];
          const noBar = bars.filter(b => b.getBoundingClientRect().width <= 0).length;
          const vds = [...document.querySelectorAll('.vd')];
          const badVd = vds.filter(e => {
            const r = e.getBoundingClientRect();
            return r.width < 200 || r.height < 80;
          }).length;
          const nulls = [...document.querySelectorAll('.vd .claim, .vd .fact, .drow .dv, .drow .dl, .wcard h4, .wcard p, .vcard q, .vcard .src, .arow .ak, .arow .rk, .lg p, .lg h4, .an p, .pth p, .wp-row .k, .wp-row .n, .wp-row .v, .pk p, .nm .l, .nm .v, .wp-fn, .wp-note p, .op p, .op .d, .op .t, .op .who, .op .act, #wp_unknown p')]
            .filter(e => /undefined|null|NaN|\[object/.test(e.textContent)).length;
          const tags = [...document.querySelectorAll('.vd .mark')].filter(e=>e.textContent.includes('核对')).length;
          const wc = [...document.querySelectorAll('.wcard')];
          const badWc = wc.filter(e => { const r=e.getBoundingClientRect(); return r.width<200||r.height<100; }).length;
          const vc = [...document.querySelectorAll('.vcard')];
          const badVc = vc.filter(e => { const r=e.getBoundingClientRect(); return r.width<220||r.height<120; }).length;
          const qOver = [...document.querySelectorAll('.vcard q, .wcard p, .lg p, .an p, .pth p')]
            .filter(e => e.scrollWidth > e.clientWidth + 2).length;
          const empts = [...document.querySelectorAll('.vcard q')].filter(e=>e.textContent.trim().length<10).length;
          const an = [...document.querySelectorAll('.an')];
          const badAn = an.filter(e => { const r=e.getBoundingClientRect(); return r.width<200||r.height<80; }).length;
          const lg = [...document.querySelectorAll('.lg')];
          const badLg = lg.filter(e => { const r=e.getBoundingClientRect(); return r.width<220||r.height<120; }).length;
          const rawHtml = [...document.querySelectorAll('.lg p, .an p, .pth p')]
            .filter(e => /<b>|<em>|<\/b>/.test(e.textContent)).length;
          // ---- 第 18 节：化债的账谁在付（严格三分）----
          const wpRows = document.querySelectorAll('#wp_plan .wp-row').length;
          const wpPk = document.querySelectorAll('#wp_pocket .pk').length;
          // 卡片数为奇数时最后一张要跨列，否则末行只占半宽
          const wideEl = document.querySelector('#wp_pocket .pk.wide');
          const wideOk = !wideEl ? true : (() => {
            const pk = document.querySelector('#wp_pocket .pk');
            return wideEl.getBoundingClientRect().width > pk.getBoundingClientRect().width * 1.6;
          })();
          const planFn = !!document.querySelector('#wp_plan .wp-fn');
          // 国家队操作时间线 / 7·17 各方动作
          const opsRows = document.querySelectorAll('#wp_ops .op').length;
          const julRows = document.querySelectorAll('#wp_july .op.jul').length;
          const opsLv = [...document.querySelectorAll('#wp_ops .lv2')].map(e=>e.textContent.trim());
          const opsSub = !!document.querySelector('#whopays .wp-sub');
          const profit = document.querySelector('#wp_profit');
          const profitLen = profit ? profit.textContent.trim().length : 0;
          const opsOver = [...document.querySelectorAll('#whopays .op')]
            .filter(e => e.scrollWidth > e.clientWidth + 2).length;
          const wpNm = document.querySelectorAll('#wp_stock .nm').length;
          const wpUk = document.querySelectorAll('#wp_unknown .uk').length;
          // 三个分区标签必须齐：已知 / 可推断 / 不可知
          const lv = [...document.querySelectorAll('#whopays .wp-lv')].map(e=>e.textContent.trim());
          // 卡片布局不能塌
          const badPk = [...document.querySelectorAll('#wp_pocket .pk')]
            .filter(e => { const r=e.getBoundingClientRect(); return r.width<200||r.height<120; }).length;
          const badUk = [...document.querySelectorAll('#wp_unknown .uk')]
            .filter(e => { const r=e.getBoundingClientRect(); return r.width<200||r.height<100; }).length;
          // 行内文字不能溢出
          const wpOver = [...document.querySelectorAll('#whopays .wp-row .k, #whopays .wp-row .v, #whopays .pk p, #whopays .nm .l, #whopays .nm .v, #whopays .wp-fn')]
            .filter(e => e.scrollWidth > e.clientWidth + 2).length;
          // 不可知栏的 <b> 必须渲染成标签而不是转义文本
          const wpBold = document.querySelectorAll('#wp_unknown p b').length;
          const wpLeak = [...document.querySelectorAll('#wp_unknown p')]
            .filter(e => /<b>|<\/b>/.test(e.textContent)).length;
          // 数值不能因为格子过窄被压成竖排：曾出现 4 列 263px 下
          // 「近 400 家 · 拟减持超 1200 亿」逐字换行。单行约 22px，允许最多两行。
          const wpSquash = [...document.querySelectorAll('#wp_stock .v, #wp_plan .v')]
            .filter(e => e.getBoundingClientRect().height > 46).length;
          return {cellOver, bars: bars.length, noBar, vds: vds.length, badVd, nulls, tags,
                  badWc, badVc, qOver, empts, badAn, badLg, rawHtml,
                  wpRows, wpPk, wpNm, wpUk, lv, badPk, badUk, wpOver, wpBold, wpLeak, wpSquash,
                  wideOk, planFn, opsRows, julRows, opsLv, opsSub, profitLen, opsOver};
        }""")
        print('  新增区块：', json.dumps({k: v for k, v in addv.items() if not k.startswith('wp') and k != 'lv'}, ensure_ascii=False))
        print('  化债三分：', json.dumps({k: v for k, v in addv.items() if k.startswith('wp') or k == 'lv'}, ensure_ascii=False))
        chk(addv['cellOver'] == 0, '对照表/数据表单元格宽度正常（异常 %d）' % addv['cellOver'])
        chk(addv['noBar'] == 0, '数据表条形全部有宽度（无宽度 %d/%d）' % (addv['noBar'], addv['bars']))
        chk(addv['badVd'] == 0, '判断核对卡片布局正常（异常 %d/%d）' % (addv['badVd'], addv['vds']))
        chk(addv['tags'] == 6, '判断核对全部带核对标签（%d/6）' % addv['tags'])
        chk(addv['nulls'] == 0, '新增区块无 undefined / null / NaN（%d）' % addv['nulls'])
        chk(addv['badWc'] == 0, '为什么卡片布局正常（异常 %d/4）' % addv['badWc'])
        chk(addv['badVc'] == 0, '观点卡片布局正常（异常 %d/6）' % addv['badVc'])
        chk(addv['qOver'] == 0, '长文本块无横向溢出（%d）' % addv['qOver'])
        chk(addv['empts'] == 0, '观点引文非空（%d）' % addv['empts'])
        chk(addv['badAn'] == 0, 'AI 类比卡片布局正常（异常 %d/4）' % addv['badAn'])
        chk(addv['badLg'] == 0, '核算卡片布局正常（异常 %d/6）' % addv['badLg'])
        chk(addv['rawHtml'] == 0, '富文本标签已渲染未转义泄漏（%d）' % addv['rawHtml'])

        # 第 18 节：化债的账谁在付 —— 严格三分（已知 / 可推断 / 不可知）
        chk(addv['wpRows'] == 7, '化债方案表 7 行（实际 %d）' % addv['wpRows'])
        chk(addv['wpPk'] == 5, '代价落在 5 个主体上（实际 %d）' % addv['wpPk'])
        chk(addv['wideOk'], '奇数张卡片时末张跨列（避免末行只占半宽）')
        chk(addv['planFn'], '化债资金来源脚注存在（纠正「中央掏钱」的误解）')
        # 国家队操作（并入本节）
        chk(addv['opsRows'] == 7, '国家队操作时间线 7 个节点（实际 %d）' % addv['opsRows'])
        chk(addv['julRows'] == 6, '7 月 17 日六方动作（实际 %d）' % addv['julRows'])
        chk(addv['opsLv'].count('份额硬数据') >= 4 and addv['opsLv'].count('含测算') >= 3,
            '时间线逐条标注证据强度（硬数据 %d / 含测算 %d）'
            % (addv['opsLv'].count('份额硬数据'), addv['opsLv'].count('含测算')))
        chk(addv['opsSub'], '7 月 17 日分节标题存在')
        chk(addv['profitLen'] > 120, '盈利测算与边界说明非空（%d 字）' % addv['profitLen'])
        chk(addv['opsOver'] == 0, '操作时间线无横向溢出（%d）' % addv['opsOver'])
        chk(addv['wpNm'] == 14, '股市与财政可观测数据 14 条（实际 %d）' % addv['wpNm'])
        chk(addv['wpUk'] == 4, '不可知清单 4 条（实际 %d）' % addv['wpUk'])
        chk(addv['lv'] == ['已知', '可推断', '可观测', '可观测', '不可知'],
            '五个分区标签齐备（实际 %s）' % '/'.join(addv['lv']))
        chk(addv['badPk'] == 0, '口袋卡片布局正常（异常 %d/5）' % addv['badPk'])
        chk(addv['badUk'] == 0, '不可知卡片布局正常（异常 %d/4）' % addv['badUk'])
        chk(addv['wpOver'] == 0, '化债新区块无横向溢出（%d）' % addv['wpOver'])
        # 不可知栏正文含 <b> 强调，必须渲染成标签、不能转义泄漏
        chk(addv['wpBold'] > 0, '不可知栏强调标签已渲染（%d 处）' % addv['wpBold'])
        chk(addv['wpLeak'] == 0, '不可知栏无转义泄漏（%d）' % addv['wpLeak'])
        chk(addv['wpSquash'] == 0, '数值未被压成竖排（异常 %d/21）' % addv['wpSquash'])

        # 新增区块：当年 vs 现在 / 未知清单 / 推理边界提示
        trk = await pg.evaluate("""() => {
          const laid = el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
          const trks = [...document.querySelectorAll('.trk')];
          const badTrk = trks.filter(e => {
            const r = e.getBoundingClientRect();
            if (r.width < 320 || r.height < 120) return true;
            const who = e.querySelector('.who'), mid = e.querySelector('.mid'), side = e.querySelector('.side');
            if (!who || !mid || !side) return true;
            return !laid(who) || !laid(mid) || !laid(side)
              || mid.getBoundingClientRect().width < 260
              || mid.getBoundingClientRect().height < 100;
          }).length;
          const pairs = [...document.querySelectorAll('.trk .pair')];
          const badPair = pairs.filter(e => !laid(e) || !e.querySelector('.tag')).length;
          const over = [...document.querySelectorAll('.trk .pair p, .trk .side .note, .uk p, .unote-b')]
            .filter(e => e.scrollWidth > e.clientWidth + 2).length;
          const uks = [...document.querySelectorAll('#ukwall .uk')];
          const badUk = uks.filter(e => {
            const r = e.getBoundingClientRect();
            return r.width < 280 || r.height < 120 || !laid(e.querySelector('.vb'));
          }).length;
          const nulls2 = [...document.querySelectorAll('.trk .pair p, .trk .dtag, .trk .note, .uk p, .uk .vb, .unote-b')]
            .filter(e => /undefined|null|NaN|\[object/.test(e.textContent)).length;
          const leaked = [...document.querySelectorAll('.trk .pair p, .uk p, .unote-b')]
            .filter(e => /<b>|<\/b>/.test(e.textContent)).length;
          return {trks: trks.length, badTrk, pairs: pairs.length, badPair, over,
                  uks: uks.length, badUk, nulls2, leaked};
        }""")
        print('  判断追踪：', json.dumps(trk, ensure_ascii=False))
        chk(trk['badTrk'] == 0, '三栏追踪卡片布局正常（异常 %d/%d）' % (trk['badTrk'], trk['trks']))
        chk(trk['badPair'] == 0, '当年/现在两组对照齐全（异常 %d/%d）' % (trk['badPair'], trk['pairs']))
        chk(trk['over'] == 0, '追踪与未知清单无横向溢出（%d）' % trk['over'])
        chk(trk['badUk'] == 0, '未知清单卡片布局正常（异常 %d/%d）' % (trk['badUk'], trk['uks']))
        chk(trk['nulls2'] == 0, '追踪区块无 undefined / null / NaN（%d）' % trk['nulls2'])
        chk(trk['leaked'] == 0, '追踪区块富文本已渲染未转义泄漏（%d）' % trk['leaked'])

        # --- 交互真点 ---
        print('\n=== 交互 · 真实点击 ===')
        await pg.click('.card')
        await pg.wait_for_timeout(500)
        dopen = await pg.evaluate("()=>document.getElementById('drawer').classList.contains('on')")
        chk(dopen, '点卡片打开详情面板')
        t1 = await pg.inner_text('#dtitle')
        para = await pg.evaluate("()=>document.querySelectorAll('#dbody p').length")
        chk(para > 5, '面板内正文段落 %d 段' % para)

        await pg.keyboard.press('ArrowRight')
        await pg.wait_for_timeout(420)
        t2 = await pg.inner_text('#dtitle')
        chk(t1 != t2, '→ 翻到下一节（%s → %s）' % (t1[:10], t2[:10]))
        await pg.keyboard.press('ArrowLeft')
        await pg.wait_for_timeout(420)
        t3 = await pg.inner_text('#dtitle')
        chk(t3 == t1, '← 翻回上一节')

        await pg.keyboard.press('Escape')
        await pg.wait_for_timeout(500)
        dclosed = await pg.evaluate("()=>!document.getElementById('drawer').classList.contains('on')")
        foc = await pg.evaluate("()=>document.activeElement && document.activeElement.classList.contains('card')")
        chk(dclosed, 'Esc 关闭面板')
        chk(foc, '关闭后焦点回到来源卡片')

        # 面板内含图的章节（7.1 有 4 图）
        await pg.click('#chips .chip[data-k="down"]')
        await pg.wait_for_timeout(260)
        n1 = await pg.evaluate("()=>document.querySelectorAll('.card').length")
        await pg.click('#chips .chip[data-k="up"]')
        await pg.wait_for_timeout(260)
        n2 = await pg.evaluate("()=>document.querySelectorAll('.card').length")
        await pg.click('#chips .chip[data-k="all"]')
        await pg.wait_for_timeout(260)
        n3 = await pg.evaluate("()=>document.querySelectorAll('.card').length")
        chk(n3 == 53 and n1 < n3 and n2 < n3, '筛选生效（上篇 %d / 下篇 %d / 全部 %d）' % (n2, n1, n3))

        await pg.fill('#q', '土地财政')
        await pg.wait_for_timeout(420)
        nq = await pg.evaluate("()=>document.querySelectorAll('.card').length")
        chk(0 < nq < 53, '搜索土地财政 命中 %d 节' % nq)
        await pg.fill('#q', 'zzzz不存在zzz')
        await pg.wait_for_timeout(420)
        empty = await pg.evaluate("()=>!!document.querySelector('.empty')")
        chk(empty, '空结果态出现')
        await pg.fill('#q', '')
        await pg.wait_for_timeout(420)

        # 灯箱
        await pg.click('#figwall .fig')
        await pg.wait_for_timeout(450)
        lb = await pg.evaluate("()=>document.getElementById('lb').classList.contains('on') && document.getElementById('lbimg').naturalWidth>0")
        chk(lb, '图表灯箱打开且大图解码')
        await pg.keyboard.press('Escape')
        await pg.wait_for_timeout(350)
        lbc = await pg.evaluate("()=>!document.getElementById('lb').classList.contains('on')")
        chk(lbc, 'Esc 关闭灯箱')

        # --- 导航交互 ---
        print('\n=== 导航 · 滚动高亮 / 进度条 / 抽屉 ===')
        await pg.set_viewport_size({'width': 1440, 'height': 940})
        # 关掉平滑滚动，让断言等待时间可控（不影响页面本身的平滑滚动）。
        # 标签条自己的 scroll-behavior:smooth 也要关——否则下面程序化赋值
        # scrollLeft 变成异步动画，读到的是中间态，渐隐类断言会假失败。
        await pg.evaluate("""() => {
          document.documentElement.style.scrollBehavior='auto';
          const s = document.getElementById('nstrip');
          if(s) s.style.scrollBehavior='auto';
        }""")
        await pg.evaluate("scrollTo(0,0)")
        await pg.wait_for_timeout(420)

        # 逐节点跳，确认高亮跟随（用点选而非滚动，滚动高亮另测）
        hl = []
        for sid in ['loop', 'chapters', 'after', 'why', 'ledger', 'whopays', 'ai']:
            await pg.evaluate("document.getElementById('%s').scrollIntoView()" % sid)
            await pg.wait_for_timeout(340)
            hl.append(await pg.evaluate("""() => {
              const a = document.querySelector('#rdot a.on');
              const s = document.querySelector('#nstrip a.on');
              const p = document.querySelector('#npop a.on');
              return {dot: a ? a.dataset.nav : null,
                      strip: s ? s.dataset.nav : null,
                      pop: p ? p.dataset.nav : null,
                      w: document.getElementById('pbar').style.width};
            }"""))
        hit = [h for h, sid in zip(hl, ['loop','chapters','after','why','ledger','whopays','ai']) if h['dot'] == sid]
        chk(len(hit) == 7, '滚动高亮跟随到位（%d/7：%s）' % (len(hit), ','.join(h['dot'] or 'null' for h in hl)))
        chk(all(h['dot'] == h['strip'] or h['strip'] is None for h in hl),
            '标签条与浮动目录高亮一致')
        chk(all(h['dot'] == h['pop'] for h in hl), '下拉目录高亮与浮动目录一致')
        ws = [float(h['w'].rstrip('%')) for h in hl if h['w']]
        chk(len(ws) >= 5 and ws[-1] > ws[0], '进度条随滚动增长（%.1f%% → %.1f%%）' % (ws[0], ws[-1]))

        # --- 标签条四组内联专项 ---
        # 之前只内联「原书精读」一组，其余 10 个区块在标签条上没有可见入口
        # 先把标签条复位到起点，否则前面滚动高亮的测试已经把它滚走了
        await pg.evaluate("const s=document.getElementById('nstrip'); s.scrollLeft=0;")
        await pg.wait_for_timeout(260)
        stb = await pg.evaluate("""() => {
          const s = document.getElementById('nstrip');
          const gl = [...s.querySelectorAll('.glab')].map(e=>e.textContent.trim());
          const items = [...s.querySelectorAll('a[data-nav]')].map(a=>a.dataset.nav);
          const groups = [...s.querySelectorAll('.sgrp')].map(g=>({
            n: g.querySelector('.glab').textContent.trim(),
            c: g.querySelectorAll('a').length}));
          const r = s.getBoundingClientRect();
          const overflow = s.scrollWidth - s.clientWidth;
          // 组名是否与组内某一项的可见文字相同（视觉上会读成重复）
          const dups = [];
          [...s.querySelectorAll('.sgrp')].forEach(g=>{
            const gn = g.querySelector('.glab').textContent.trim();
            [...g.querySelectorAll('a')].forEach(a=>{
              if(a.textContent.trim() === gn) dups.push(gn);
            });
          });
          return {gl, items, groups, overflow, dups,
                  cls: s.className,
                  sl: Math.round(s.scrollLeft),
                  fits: overflow <= 2};
        }""")
        print('  标签条：', json.dumps({k: v for k, v in stb.items() if k != 'items'}, ensure_ascii=False))
        # 组名不能与组内区块名重复（曾出现「书成之后」组里套一个「书成之后」项）
        chk(stb['gl'] == ['原书精读', '书写完之后', '决策溯源', '判断与现状'],
            '标签条按顺序内联 4 组（实际 %s）' % '/'.join(stb['gl']))
        dup = stb['dups']
        chk(not dup, '组名不与组内区块名重复（重复：%s）' % ','.join(dup))
        chk([g['c'] for g in stb['groups']] == [8, 2, 2, 7],
            '标签条各组项数 8/2/2/7（实际 %s）' % '/'.join(str(g['c']) for g in stb['groups']))
        chk(len(set(stb['items'])) == 19,
            '标签条覆盖全部 19 个区块（实际 %d）' % len(set(stb['items'])))
        # 在起点：只显示右侧渐隐（提示右边还有内容），不应显示左侧
        if stb['overflow'] > 2:
            chk('ovR' in stb['cls'].split(),
                '标签条溢出时右侧渐隐生效（溢出 %dpx，cls=%s）' % (stb['overflow'], stb['cls']))
            chk('ovL' not in stb['cls'].split(),
                '标签条在起点时不显示左侧渐隐（cls=%s）' % stb['cls'])
            # 滚到末端：渐隐翻到左侧
            await pg.evaluate("const s=document.getElementById('nstrip'); s.scrollLeft=99999;")
            await pg.wait_for_timeout(300)
            endcls = await pg.evaluate("document.getElementById('nstrip').className")
            chk('ovL' in endcls.split() and 'ovR' not in endcls.split(),
                '标签条滚到末端时渐隐翻到左侧（cls=%s）' % endcls)
            await pg.evaluate("const s=document.getElementById('nstrip'); s.scrollLeft=0;")
            await pg.wait_for_timeout(220)
        else:
            chk('ovR' not in stb['cls'].split() and 'ovL' not in stb['cls'].split(),
                '标签条未溢出时不显示渐隐')
        # 滚到「判断与现状」组（标签条末端）时，当前项应自动滚进视野。
        # 注意：不能只调 scrollIntoView('ai')，因为区块没变时不会触发 scroll
        # 事件、sync() 不跑。真实场景是「用户滚动页面」，所以先滚到别处再滚过来。
        await pg.evaluate("document.getElementById('loop').scrollIntoView()")
        await pg.wait_for_timeout(420)
        await pg.evaluate("document.getElementById('ai').scrollIntoView()")
        await pg.wait_for_timeout(620)
        vis = await pg.evaluate("""() => {
          const s = document.getElementById('nstrip');
          const a = s.querySelector('a[data-nav="ai"]');
          if(!a) return {ok:false};
          const sr = s.getBoundingClientRect(), ar = a.getBoundingClientRect();
          return {ok: ar.left >= sr.left - 1 && ar.right <= sr.right + 1,
                  sl: Math.round(s.scrollLeft),
                  max: s.scrollWidth - s.clientWidth,
                  aIn: a.classList.contains('on')};
        }""")
        print('  标签条跟随：', json.dumps(vis, ensure_ascii=False))
        chk(vis.get('aIn'), '滚到 AI 区块时标签条当前项高亮')
        if stb['overflow'] > 2:
            chk(vis.get('sl', 0) > 0,
                '溢出时当前项自动滚入视野（scrollLeft=%d / max=%d）'
                % (vis.get('sl', -1), vis.get('max', -1)))
            chk(vis.get('ok'), '自动滚动后当前项完整落在可视区内')
            # 窗口尺寸变化（未换区块）时也要重新定位，不能因为「区块没变」就跳过
            await pg.set_viewport_size({'width': 1000, 'height': 900})
            await pg.wait_for_timeout(520)
            vw = await pg.evaluate("""() => {
              const s = document.getElementById('nstrip');
              const a = s.querySelector('a[data-nav="ai"]');
              if(!a) return {ok:false};
              const sr = s.getBoundingClientRect(), ar = a.getBoundingClientRect();
              return {ok: ar.left >= sr.left - 1 && ar.right <= sr.right + 1,
                      sl: Math.round(s.scrollLeft),
                      max: s.scrollWidth - s.clientWidth};
            }""")
            print('  变宽后：', json.dumps(vw, ensure_ascii=False))
            chk(vw.get('ok'), '视口变窄且未换区块时当前项仍完整可见（scrollLeft=%d）' % vw.get('sl', -1))
            await pg.set_viewport_size({'width': 1440, 'height': 940})
            await pg.wait_for_timeout(420)
        # --- 标签条当前项居中专项 ---
        # 旧逻辑只「滚到刚好可见」，当前项会一直贴在标签条最右边；现要求居中。
        # 例外：第一项左边没内容、末项右边没内容，物理上无法居中，只能贴边（clamp）。
        # 关掉标签条自身的 smooth，让 scrollLeft 赋值同步生效，断言等待时间可控。
        await pg.evaluate("const s=document.getElementById('nstrip'); s.style.scrollBehavior='auto'; s.scrollLeft=0;")
        await pg.wait_for_timeout(200)
        cent = []
        for sid in ['loop', 'why', 'views', 'whopays', 'ai']:
            await pg.evaluate("document.getElementById('%s').scrollIntoView()" % sid)
            await pg.wait_for_timeout(420)
            cent.append(await pg.evaluate("""(sid) => {
              const s = document.getElementById('nstrip');
              const a = s.querySelector('a[data-nav="'+sid+'"]');
              if(!a) return {sid: sid, off: null, clamped: false, centered: false};
              const sr = s.getBoundingClientRect(), ar = a.getBoundingClientRect();
              const max = s.scrollWidth - s.clientWidth;
              const off = Math.round((ar.left+ar.width/2)-(sr.left+sr.width/2));
              return {sid: sid, sl: Math.round(s.scrollLeft), max: Math.round(max),
                      off: off, centered: Math.abs(off) <= 12,
                      clamped: s.scrollLeft <= 2 || s.scrollLeft >= max - 2};
            }""", sid))
        for r in cent:
            print('  居中：', json.dumps(r, ensure_ascii=False))
        bad = [r['sid'] for r in cent if not (r['centered'] or r['clamped'])]
        chk(not bad, '标签条当前项居中，不可居中时贴边（异常：%s）' % (','.join(bad) or '无'))
        mid = [r for r in cent if r['sid'] in ('why', 'views')]
        chk(all(r['centered'] for r in mid),
            '中部区块当前项偏差≤12px（%s）'
            % ' '.join('%s %+dpx' % (r['sid'], r['off']) for r in mid))
        # 进度条在底部应接近 100
        await pg.evaluate("document.documentElement.style.scrollBehavior='auto'; scrollTo(0, 9999999)")
        await pg.wait_for_timeout(700)
        wend = await pg.evaluate("parseFloat(document.getElementById('pbar').style.width)")
        atbot = await pg.evaluate("scrollY + innerHeight >= document.documentElement.scrollHeight - 3")
        chk(atbot, '已滚到页面底部')
        chk(wend > 96, '滚到底进度条接近 100%%（实际 %.1f%%）' % wend)

        # 下拉菜单开合
        await pg.evaluate("scrollTo(0,0)"); await pg.wait_for_timeout(300)
        await pg.click('#nmore > button'); await pg.wait_for_timeout(280)
        dpop = await pg.evaluate("""() => {
          const p = document.getElementById('npop');
          const r = p.getBoundingClientRect();
          const vis = getComputedStyle(p).display !== 'none' && r.width > 150 && r.height > 100;
          const link = [...p.querySelectorAll('a')].length;
          const inView = r.right <= innerWidth + 1 && r.left >= -1;
          // 关键：下拉不能被任何祖先裁剪（nav 曾用 overflow:hidden 修窄屏溢出，把下拉切没了）
          let clippedBy = null, a = p.parentElement;
          while(a){ const o = getComputedStyle(a);
            if(o.overflow !== 'visible' || o.overflowX !== 'visible' || o.overflowY !== 'visible'){ clippedBy = a.id || a.className; break; }
            a = a.parentElement; }
          // 下拉底边必须在视口内（避免长菜单被挤出去）
          const fitsH = r.bottom <= innerHeight + 1 || getComputedStyle(p).overflowY === 'auto';
          return {vis, link, inView, clippedBy, fitsH};
        }""")
        chk(dpop['vis'], '点击「全部章节」弹出下拉')
        chk(dpop['link'] == 19, '下拉 19 项可见（%d）' % dpop['link'])
        chk(dpop['inView'], '下拉未超出视口右边界')
        chk(dpop['clippedBy'] is None,
            '下拉未被祖先 overflow 裁剪（被 %s 裁剪）' % dpop['clippedBy'])
        chk(dpop['fitsH'], '下拉底边在视口内或可滚动')
        await pg.screenshot(path=os.path.join(SHOT, 'N2_nav_pop.png'))
        await pg.click('#npop a[data-nav="track"]')
        await pg.wait_for_timeout(140)
        closed = await pg.evaluate("!document.getElementById('nmore').classList.contains('on')")
        chk(closed, '点下拉项后自动收起')
        await pg.wait_for_timeout(700)
        jumped = await pg.evaluate("Math.abs(document.getElementById('track').getBoundingClientRect().top) < 130")
        chk(jumped, '下拉跳转到目标区块')

        # 断点两侧：>760px 标签条在、汉堡按钮不在；<=760px 反过来
        for vw, want in [(900, True), (761, True), (760, False), (600, False)]:
            await pg.set_viewport_size({'width': vw, 'height': 880})
            await pg.wait_for_timeout(360)
            bp = await pg.evaluate("""() => ({
              strip: getComputedStyle(document.getElementById('nstrip')).display !== 'none',
              burger: getComputedStyle(document.getElementById('burger')).display !== 'none',
              hScroll: document.documentElement.scrollWidth - document.documentElement.clientWidth,
            })""")
            chk(bp['strip'] == want and bp['burger'] == (not want),
                '%dpx 标签条%s / 汉堡%s' % (vw, '在' if want else '隐藏', '隐藏' if want else '在'))
            chk(bp['hScroll'] == 0, '%dpx 无横向溢出（%d）' % (vw, bp['hScroll']))
        await pg.set_viewport_size({'width': 1440, 'height': 940})
        await pg.wait_for_timeout(320)

        # 移动端抽屉
        await pg.set_viewport_size({'width': 390, 'height': 880})
        await pg.wait_for_timeout(420)
        mvis = await pg.evaluate("""() => ({
          burger: getComputedStyle(document.getElementById('burger')).display !== 'none',
          strip: getComputedStyle(document.getElementById('nstrip')).display,
          dots: getComputedStyle(document.getElementById('rdot')).display === 'none',
          more: getComputedStyle(document.getElementById('nmore')).display,
        })""")
        chk(mvis['burger'], '390px 汉堡按钮可见')
        chk(mvis['dots'], '390px 浮动目录隐藏')
        chk(mvis['strip'] == 'none', '390px 标签条隐藏（实际 %s）' % mvis['strip'])
        # 标签条隐藏后「全部章节」应紧跟汉堡按钮，不能被空白隔开
        gap = await pg.evaluate("""() => {
          const b = document.getElementById('burger').getBoundingClientRect();
          const m = document.getElementById('nmore').getBoundingClientRect();
          return Math.round(m.left - b.right);
        }""")
        chk(0 <= gap < 60, '390px 全部章节紧跟汉堡按钮（间距 %dpx）' % gap)
        await pg.click('#burger'); await pg.wait_for_timeout(420)
        draw = await pg.evaluate("""() => {
          const m = document.getElementById('mnav'), p = m.querySelector('.pn');
          const r = p.getBoundingClientRect();
          return {on: m.classList.contains('on'), left: Math.round(r.left),
                  w: Math.round(r.width), links: p.querySelectorAll('a[data-nav]').length,
                  locked: document.body.style.overflow === 'hidden'};
        }""")
        chk(draw['on'] and draw['left'] == 0 and draw['w'] > 200, '抽屉滑入到位（left=%d w=%d）' % (draw['left'], draw['w']))
        chk(draw['links'] == 19, '抽屉内 19 项（%d）' % draw['links'])
        chk(draw['locked'], '抽屉打开时锁定页面滚动')

        # 浮点目录：必须高于导航条，不能被任何元素遮挡
        # （nav 是 sticky，静止位在 hero 之后，滚到顶部时正好横穿浮点目录区域）
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(400)
        chk(await pg.evaluate("!document.getElementById('mnav').classList.contains('on')"),
            'Esc 关闭抽屉')
        chk(await pg.evaluate("document.body.style.overflow !== 'hidden'"),
            '关闭抽屉后恢复页面滚动')

        await pg.set_viewport_size({'width': 1440, 'height': 940})
        await pg.evaluate("scrollTo(0,0)"); await pg.wait_for_timeout(500)
        zz = await pg.evaluate("""() => {
          const d = document.getElementById('rdot'), r = d.getBoundingClientRect();
          const dz = +getComputedStyle(d).zIndex;
          const nz = +getComputedStyle(document.querySelector('nav')).zIndex;
          // 沿浮点目录的竖直中轴取样，看有没有别的元素压在上面
          const blockers = [];
          for(let y = Math.round(r.top) + 2; y < r.bottom - 2; y += 5){
            const el = document.elementFromPoint(Math.round(r.left + r.width/2), y);
            if(el && !d.contains(el)){
              blockers.push((el.closest('nav') ? 'nav>' : '') + el.tagName +
                            '.' + (typeof el.className === 'string' ? el.className.slice(0,24) : ''));
            }
          }
          return {dz, nz, blockers: [...new Set(blockers)],
                  navBg: getComputedStyle(document.querySelector('nav')).backgroundColor,
                  stuck: document.querySelector('nav').classList.contains('stuck'),
                  top: Math.round(r.top), bottom: Math.round(r.bottom)};
        }""")
        print('  浮点目录层级：', json.dumps(zz, ensure_ascii=False))
        chk(zz['dz'] > zz['nz'], '浮动目录层级高于导航条（%d > %d）' % (zz['dz'], zz['nz']))
        chk(not zz['blockers'], '浮动目录全段无遮挡（被遮挡：%s）' % ','.join(zz['blockers']))
        # 页面滚到顶时导航条处于静止位（未粘顶），必须是透明的，
        # 否则会在 hero 区形成一条横带并与浮点目录互相干扰
        chk(not zz['stuck'], '滚到顶时导航条判为未粘顶')
        chk('rgba(0, 0, 0, 0)' in zz['navBg'],
            '未粘顶时导航条透明无横带（实际 %s）' % zz['navBg'])
        # 滚下去之后必须恢复背景，否则内容会从导航条后面透出来
        await pg.evaluate("scrollTo(0, 1600)"); await pg.wait_for_timeout(450)
        sz2 = await pg.evaluate("""() => ({
          stuck: document.querySelector('nav').classList.contains('stuck'),
          bg: getComputedStyle(document.querySelector('nav')).backgroundColor,
          top: Math.round(document.querySelector('nav').getBoundingClientRect().top)})""")
        print('  粘顶后：', json.dumps(sz2, ensure_ascii=False))
        chk(sz2['stuck'] and sz2['top'] <= 1, '滚动后导航条粘顶（top=%d）' % sz2['top'])
        chk('rgba(0, 0, 0, 0)' not in sz2['bg'], '粘顶后导航条恢复背景（%s）' % sz2['bg'])

        await pg.set_viewport_size({'width': 390, 'height': 880})
        await pg.wait_for_timeout(360)
        await pg.click('#burger'); await pg.wait_for_timeout(400)
        await pg.click('#mb a[data-nav="nowdata"]'); await pg.wait_for_timeout(700)
        chk(await pg.evaluate("!document.getElementById('mnav').classList.contains('on')"),
            '点抽屉内项后自动关闭')
        chk(await pg.evaluate("Math.abs(document.getElementById('nowdata').getBoundingClientRect().top) < 130"),
            '抽屉跳转到目标区块')

        # --- 触控目标尺寸（手机可用性）---
        # 曾出现详情面板的 ← → ✕ 只有 30x30，手机上点不准，
        # 「下一节」和「关闭」挨着时容易把关闭点成翻页。
        await pg.evaluate("scrollTo(0,0)"); await pg.wait_for_timeout(300)
        await pg.click('.card'); await pg.wait_for_timeout(600)
        tp = await pg.evaluate("""() => {
          const box = id => {
            const r = document.getElementById(id).getBoundingClientRect();
            return {w: Math.round(r.width), h: Math.round(r.height),
                    l: Math.round(r.left), r: Math.round(r.right)};
          };
          const prev = box('dprev'), next = box('dnext'), close = box('dclose');
          // 标题文字（用 Range 取真实文字范围，不能用 h3 的盒子宽度，
          // 盒子的 right 含 padding-right，会误判为重叠）
          const h3 = document.querySelector('.dh h3');
          const rg = document.createRange(); rg.selectNodeContents(h3);
          const tr = rg.getBoundingClientRect();
          const nr = document.querySelector('.dh .nav').getBoundingClientRect();
          // 标题可用宽度：不能为了给按钮让位而被压窄
          // （曾出现 393px 下只剩 167px、标题断成「前言 从了 / 解现状开始」）
          const dh = document.querySelector('.dh');
          const dhcs = getComputedStyle(dh);
          const h3cs = getComputedStyle(h3);
          const dhInner = dh.getBoundingClientRect().width
                        - parseFloat(dhcs.paddingLeft) - parseFloat(dhcs.paddingRight);
          const h3Content = h3.getBoundingClientRect().width - parseFloat(h3cs.paddingRight);
          const lines = Math.round(tr.height / parseFloat(h3cs.lineHeight));
          return {prev, next, close,
                  gapPN: next.l - prev.r,
                  gapNC: close.l - next.r,
                  textRight: Math.round(tr.right), navLeft: Math.round(nr.left),
                  overlap: Math.round(tr.right) > nr.left && Math.round(tr.bottom) > nr.top,
                  ratio: +(h3Content / dhInner).toFixed(3),
                  lines,
                  minTap: [prev, next, close].reduce((m, r) => Math.min(m, r.w, r.h), 999)};
        }""")
        print('  触控目标：', json.dumps(tp, ensure_ascii=False))
        chk(tp['minTap'] >= 42,
            '窄屏翻页/关闭按钮 ≥42px（实际 %dx%d）' % (tp['prev']['w'], tp['prev']['h']))
        chk(tp['gapPN'] >= 8 and tp['gapNC'] >= 8,
            '翻页/关闭按钮间距 ≥8px 防误点（%d / %d）' % (tp['gapPN'], tp['gapNC']))
        chk(not tp['overlap'],
            '详情标题不与翻页按钮重叠（文字右 %d / 按钮左 %d）'
            % (tp['textRight'], tp['navLeft']))
        chk(tp['ratio'] >= 0.85,
            '窄屏标题可用宽度 ≥85%% 面板内宽（实际 %.1f%%）' % (tp['ratio'] * 100))
        # 全页扫描：任何可见可点元素都不应小于 32px
        tap = await pg.evaluate("""() => {
          return [...document.querySelectorAll('a,button')].filter(e => {
            const q = e.getBoundingClientRect();
            if(q.width === 0 || q.height === 0) return false;
            return q.height < 32 || q.width < 32;
          }).map(e => e.tagName + '.' + String(e.className||'').slice(0,20)
                      + '(' + Math.round(e.getBoundingClientRect().width) + 'x'
                      + Math.round(e.getBoundingClientRect().height) + ')');
        }""")
        chk(not tap, '窄屏无可点元素小于 32px（过小：%s）' % ','.join(tap))

        # 第 18 节在窄屏：方案表首列固定 190px 会横向溢出，须改为堆叠
        wpm = await pg.evaluate("""() => {
          const over = [...document.querySelectorAll('#whopays .wp-row, #whopays .pk, #whopays .nm, #whopays .uk')]
            .filter(e => e.scrollWidth > e.clientWidth + 2)
            .map(e => e.className + '(' + e.scrollWidth + '>' + e.clientWidth + ')');
          const squash = [...document.querySelectorAll('#whopays .v, #whopays .wp-row .v')]
            .filter(e => e.getBoundingClientRect().height > 46).length;
          return {over, squash,
                  rowCols: getComputedStyle(document.querySelector('.wp-row')).gridTemplateColumns};
        }""")
        print('  化债窄屏：', json.dumps(wpm, ensure_ascii=False))
        chk(not wpm['over'], '窄屏化债区块无横向溢出（溢出：%s）' % ','.join(wpm['over']))
        chk(wpm['squash'] == 0, '窄屏化债数值未被压成竖排（%d）' % wpm['squash'])
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)

        await pg.set_viewport_size({'width': 1440, 'height': 940})
        await pg.wait_for_timeout(300)

        print('\n=== 第二层 · 几何断言（居中） ===')
        for vw in [390, 1024, 1440]:
            await pg.set_viewport_size({'width': vw, 'height': 900})
            await pg.wait_for_timeout(300)
            await pg.click('.card')
            await pg.wait_for_timeout(600)
            g = await pg.evaluate("""() => {
              const d=document.querySelector('.drawer');
              const r=d.getBoundingClientRect();
              return {offCenter: Math.round((r.left+r.width/2) - innerWidth/2),
                      gapLeft: Math.round(r.left), gapRight: Math.round(innerWidth-r.right),
                      radius: getComputedStyle(d).borderRadius,
                      hScroll: document.documentElement.scrollWidth - document.documentElement.clientWidth};
            }""")
            print('  %dpx ->' % vw, json.dumps(g, ensure_ascii=False))
            if vw > 620:
                chk(abs(g['offCenter']) <= 1, '%dpx 面板水平居中（偏移 %d）' % (vw, g['offCenter']))
                chk(abs(g['gapLeft'] - g['gapRight']) <= 1, '%dpx 两侧留白对称（%d/%d）' % (vw, g['gapLeft'], g['gapRight']))
                chk(g['radius'].startswith('16px'), '%dpx 宽屏圆角 16px' % vw)
            else:
                chk(g['gapLeft'] == 0 and g['gapRight'] == 0, '%dpx 窄屏铺满' % vw)
                chk(g['radius'] in ('0px',), '%dpx 窄屏圆角退化为 0' % vw)
            chk(g['hScroll'] == 0, '%dpx 无横向溢出' % vw)
            await pg.keyboard.press('Escape')
            await pg.wait_for_timeout(420)

        print('\n=== 第三层 · 时序断言（逐帧采样） ===')
        await pg.set_viewport_size({'width': 1440, 'height': 940})
        await pg.wait_for_timeout(300)
        trace = await pg.evaluate("""async () => {
          const d=document.querySelector('.drawer');
          const sc=document.getElementById('scrim');
          const card=document.querySelector('.card');
          const frames=[]; let stop=false;
          const sample=()=>{ const r=d.getBoundingClientRect();
            const m=new DOMMatrix(getComputedStyle(d).transform==='none'?'':getComputedStyle(d).transform);
            frames.push({tx:+m.m41.toFixed(2), ty:+m.m42.toFixed(2), left:+r.left.toFixed(1), op:+getComputedStyle(d).opacity.slice(0,4)});
            if(!stop) requestAnimationFrame(sample); };
          requestAnimationFrame(sample);
          card.click();
          await new Promise(r=>setTimeout(r,1400));
          stop=true;
          return frames;
        }""")
        maxTx = max(abs(f['tx']) for f in trace)
        lefts = set(f['left'] for f in trace)
        tys = [f['ty'] for f in trace]
        print('  帧数 %d，tx 最大绝对值 %.2f，left 取值 %s，ty 起手 %.1f → 落点 %.1f' %
              (len(trace), maxTx, sorted(lefts)[:4], tys[0], tys[-1]))
        chk(maxTx == 0, '居中面板开合全程无水平位移（max|tx|=%.2f）' % maxTx)
        chk(len(lefts) == 1, '面板 left 全程恒定（%d 个取值）' % len(lefts))
        chk(tys[0] > 0, '入场为垂直浮起（起手 ty=%.1f>0）' % tys[0])
        await pg.keyboard.press('Escape')
        await pg.wait_for_timeout(450)

        print('\n=== 第四层 · 引用校验（回源比对） ===')
        src = r'D:\MyFileSystem\000-Inbox-中转站\020-Download-下载\置身事内：中国政府与经济发展 (兰小欢) (z-library.sk, 1lib.sk, z-lib.sk).epub'
        z = zipfile.ZipFile(src)
        corpus = ''
        for n in z.namelist():
            if n.startswith('OEBPS/Text/'):
                raw = z.read(n).decode('utf-8', 'ignore')
                corpus += re.sub(r'\s+', '', html.unescape(re.sub(r'<[^>]+>', '', raw)))

        def norm(s):
            s = s.replace('\u3000', '')
            s = re.sub(r'\s', '', s)
            for ch in '“”「」‘’『』"':
                s = s.replace(ch, '"')
            s = s.replace('……', '...').replace('…', '...').replace('——', '--')
            return s
        C = norm(corpus)

        # 从渲染后的页面抓取所有引句与各章标题
        page_quotes = await pg.evaluate("()=>[...document.querySelectorAll('.qt p')].map(e=>e.textContent)")
        page_ranks = await pg.evaluate("()=>[...document.querySelectorAll('.rank-row .lb')].map(e=>e.textContent)")

        bad = []
        for q in page_quotes:
            if norm(q) not in C:
                bad.append(q[:40])
        print('  金句 %d 条，逐字命中 %d 条' % (len(page_quotes), len(page_quotes) - len(bad)))
        for x in bad: print('    未命中:', x)
        chk(not bad, '全部金句在原文中逐字存在')

        # 关键数据点校验
        KEY = ['2018年末，我国的债务总量达到了GDP的258%', '居民最终消费占比只有44%',
               '中央占全国预算收入的比重从改革前的22%一跃变成55%',
               '2009年激增至8000余家', '2019年末外债余额占GDP的比重只有14%',
               '名义GDP增长了242倍', '光伏组件的价格在过去十年（2010—2019）下降了85%']
        miss = [k for k in KEY if norm(k) not in C]
        print('  关键数据点 %d 项，命中 %d 项' % (len(KEY), len(KEY) - len(miss)))
        for m in miss: print('    未命中:', m)
        chk(not miss, '关键数据点与原文一致')

        print('\n=== console / pageerror ===')
        print('  错误数：', len(errs))
        for e in errs[:12]: print('   ', e)
        chk(not errs, '无 console 错误与 pageerror')

        # 截图（按区块，不用 full_page）
        await pg.set_viewport_size({'width': 1440, 'height': 940})
        await pg.wait_for_timeout(300)
        for sel, name in [('.hero', '01_hero'), ('#loop', '02_loop'), ('#prin', '03_prin'),
                          ('#figs', '04_figs'), ('#rank', '05_rank'), ('#myth', '06_myth'),
                          ('#tl', '07_tl'), ('#cards', '08_cards'), ('#quote', '09_quote'),
                          ('#after', '09b_after'), ('#cover', '10_cover'),
                          ('#why', '11_why'), ('#views', '12_views'),
                          ('#ledger', '13_ledger'), ('#track', '13b_track'),
                          ('#unknown', '13c_unknown'),
                          ('#verdict', '14_verdict'),
                          ('#nowdata', '15_nowdata'), ('#dt_debt', '16_debt'),
                          ('#whopays', '18_whopays'),
                          ('#ai', '19_ai')]:
            try:
                await pg.locator(sel).first.scroll_into_view_if_needed()
                await pg.wait_for_timeout(320)
                await pg.locator(sel).first.screenshot(path=os.path.join(SHOT, name + '.png'))
            except Exception as ex:
                print(' 截图失败', sel, ex)
        # 面板打开态
        await pg.locator('#cards').scroll_into_view_if_needed()
        await pg.wait_for_timeout(300)
        await pg.click('.card')
        await pg.wait_for_timeout(700)
        await pg.screenshot(path=os.path.join(SHOT, '10_drawer.png'))
        await pg.keyboard.press('Escape')
        await pg.wait_for_timeout(500)

        # 导航三态
        await pg.evaluate("document.documentElement.style.scrollBehavior='auto'")
        await pg.set_viewport_size({'width': 1440, 'height': 940})
        await pg.evaluate("document.getElementById('unknown').scrollIntoView(); scrollBy(0,-70)")
        await pg.wait_for_timeout(500)
        await pg.screenshot(path=os.path.join(SHOT, 'N1_nav_wide.png'))
        await pg.set_viewport_size({'width': 390, 'height': 880})
        await pg.evaluate("scrollTo(0,0)"); await pg.wait_for_timeout(400)
        await pg.click('#burger'); await pg.wait_for_timeout(450)
        await pg.screenshot(path=os.path.join(SHOT, 'N3_nav_drawer.png'))
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(350)
        # 几何三档
        for vw in [390, 1024, 1440]:
            await pg.set_viewport_size({'width': vw, 'height': 900})
            await pg.wait_for_timeout(450)
            await pg.screenshot(path=os.path.join(SHOT, '11_geom_%d.png' % vw))

        await b.close()

    print('\n================ 结果 ================')
    if fail:
        print('失败 %d 项：' % len(fail))
        for f in fail: print(' -', f)
        sys.exit(1)
    print('全部通过')

asyncio.run(main())
