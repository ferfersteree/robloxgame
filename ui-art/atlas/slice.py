import cv2, numpy as np, json, os, sys
SH = {
 'hud_icons': (41, ['ic_coin','ic_power','ic_bag','ic_star','ic_shop','ic_bag2','ic_spear','ic_deer','ic_quests','ic_pass','ic_gear','ic_potion'], 200),
 'hud_frames': (9, ['chip_gold','chip_red','chip_blue','chip_violet','btn_red','btn_blue','btn_orange','btn_green','btn_purple','btn_yellow','btn_grey','slot','slot_sel','bar_track','bar_green','bar_cyan','bar_purple','badge'], 0),
 'hud_panels': (9, ['panel_menu','panel_quests'], 0),
 'shop_frames': (9, ['shop_header','btn_x','btn_buy','tile_orange','tile_purple','tile_blue','tile_red','tile_green','leaves','chip_dark','timer'], 0),
 'shop_icons': (25, ['potion_sun','potion_clover','potion_hands','potion_target','potion_people','coins_satchel','coins_crate','coins_chest','coins_vault','starter','charm','insight','broker','smith','wrap','vip','founder','egg_forest','egg_amber','egg_tide'], 200),
 'pass_icons': (25, ['p_coins','p_power','p_egg_forest','p_egg_amber','p_egg_storm','p_potion','p_free','p_premium','p_lock','p_check','p_paw','p_dumbbell','p_rope','p_target','p_calendar','p_clock','p_tag','p_aura','p_fair','p_dice'], 200),
 'pass_frames': (9, ['shield','tile_free','tile_premium','pennant','p_x','xp_track','xp_fill','btn_big','row_cream','chip_xp','wood_panel'], 0),
}
os.makedirs('sprites', exist_ok=True)
out = {}
for name, (dil, names, maxdim) in SH.items():
    im = cv2.imread(name + '.png', cv2.IMREAD_UNCHANGED)
    a = im[..., 3]
    mask = (a > 24).astype(np.uint8)
    k = np.ones((dil, dil), np.uint8)
    big = cv2.dilate(mask, k)
    n, lab, st, cen = cv2.connectedComponentsWithStats(big, 8)
    comps = []
    for i in range(1, n):
        m = (lab == i) & (mask > 0)
        ys, xs = np.nonzero(m)
        if len(xs) < 300: continue
        comps.append([xs.min(), ys.min(), xs.max() + 1, ys.max() + 1])
    # ряды: по центру Y
    comps.sort(key=lambda c: (c[1] + c[3]) / 2)
    rows = []
    for c in comps:
        cy = (c[1] + c[3]) / 2
        if rows and abs(cy - rows[-1]['cy']) < max(60, (c[3] - c[1]) * 0.5):
            rows[-1]['items'].append(c); rows[-1]['cy'] = np.mean([(q[1] + q[3]) / 2 for q in rows[-1]['items']])
        else:
            rows.append({'cy': cy, 'items': [c]})
    ordered = []
    for r in rows:
        ordered += sorted(r['items'], key=lambda c: c[0])
    print(name, 'found', len(ordered), 'expected', len(names), [len(r['items']) for r in rows])
    if len(ordered) != len(names):
        for c in ordered: print('   ', c)
        continue
    for nm, (x0, y0, x1, y1) in zip(names, ordered):
        sp = im[y0:y1, x0:x1].copy()
        h, w = sp.shape[:2]
        if maxdim and max(w, h) > maxdim:
            s = maxdim / max(w, h)
            sp = cv2.resize(sp, (max(1, round(w * s)), max(1, round(h * s))), interpolation=cv2.INTER_AREA)
        cv2.imwrite('sprites/%s.png' % nm, sp)
        out[nm] = sp.shape[1::-1]
        print('   %-14s %dx%d' % (nm, sp.shape[1], sp.shape[0]))
for nm, w in (('pass_header', 1024), ('shop_banner', 1024)):
    im = cv2.imread(nm + '.png', cv2.IMREAD_UNCHANGED)
    h0, w0 = im.shape[:2]; s = w / w0
    sp = cv2.resize(im, (w, round(h0 * s)), interpolation=cv2.INTER_AREA)
    cv2.imwrite('sprites/%s.png' % nm, sp); print(nm, sp.shape[1], sp.shape[0])
