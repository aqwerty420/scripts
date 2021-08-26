"""
 ______  ______   __   __   ______   __  __   ______    
/\  == \/\  __ \ /\ "-.\ \ /\  ___\ /\ \_\ \ /\  ___\   
\ \  _-/\ \ \/\ \\ \ \-.  \\ \ \____\ \  __ \\ \  __\   
 \ \_\   \ \_____\\ \_\\"\_\\ \_____\\ \_\ \_\\ \_____\ 
  \/_/    \/_____/ \/_/ \/_/ \/_____/ \/_/\/_/ \/_____/ 
                                   

Changelog :

v0.1 Initial release

v0.2 Fix for dagger wait & R cancel

v0.3 Fix for KS which could cause a variety of bugs & Jpeg fixed crash at lvl 18 <3

v0.4 Added R cancel if we can kill

v0.41 Small fix

v0.42 Fixed perma E in KS

TO_DO :

Add Ignite KS
Add missing KS COMBO

"""

from valkyrie import *
from helpers.damages import *
import copy
from helpers.flags import Orbwalker
from helpers.targeting import *
from time import time

target_selector = TargetSelector(0, TargetSet.Champion)


passive_width = 200
passive_hit_width = 280

ks_module = True
ks_restrict_combo = False
q_ks = True
w_ks = True
e_ks = True
r_ks = True
er_ks_tower = True
r_ks_value = 80
e_ks_tower = True

combo_module = True
q_combo = True
w_combo = True
w_combo_close = True
w_combo_range = 240
e_combo = True
e_wait_combo = True
e_combo_tower = False
r_combo = True
r_combo_value = 3

harass_module = False
q_harass = False
q_harass_tower = False

r_auto_cancel = True
escape_tower = True

q_delay = 0.250
q_range = 625

w_delay = 0.250

e_delay = 0.15
e_range_enemy = 725
e_range_dagger = 775

r_width = 440
r_auto_ks = True

fight_range = 1500
include_clones = True
tower_range = 925

dagger_draw = True
dagger_circle = 90
dagger_pts = 20
dagger_thickness = 5.0
dagger_color = Col.Red
dagger_onground_color = Col.Purple

q_throw = False


class Dagger:

    def __init__(self, missile, player_pos) -> None:
        self.id = missile.net_id
        missile.spell.end_pos.clone()
        self.pos = Vec3(missile.spell.end_pos.x,
                        player_pos.y, missile.spell.end_pos.z)
        self.timestamp = 0.0
        self.onground = False

    def is_expired(self, timestamp):
        return self.timestamp + 4.0 < timestamp


daggers: list[Dagger] = []


def valkyrie_menu(ctx: Context):
    global r_auto_ks, r_width, e_wait_combo, dagger_draw, dagger_circle, dagger_pts, dagger_thickness, dagger_color, dagger_onground_color, w_combo_close, w_combo_range, escape_tower, r_auto_cancel, e_combo_tower, er_ks_tower, w_ks, e_ks_tower, r_combo_value, r_ks_value, include_clones, harass_module, q_harass, q_harass_tower, ks_module, ks_restrict_combo, q_ks, e_ks, r_ks, combo_module, q_combo, w_combo, e_combo, r_combo
    ui = ctx.ui

    ui.text("Ponche Katarina 0.42")
    ui.separator()

    include_clones = ui.checkbox('Include clones', include_clones)
    ui.separator()

    if ui.beginmenu("Draw"):
        dagger_draw = ui.checkbox('Enabled', dagger_draw)
        dagger_circle = ui.sliderint("Circle size", dagger_circle, 1, 160)
        dagger_pts = ui.sliderint("Circle pts number", dagger_pts, 4, 220)
        dagger_thickness = ui.sliderfloat(
            "Circle thickness", dagger_thickness, 1.0, 10.0)
        dagger_color = ui.colorpick("Color", dagger_color)
        dagger_onground_color = ui.colorpick(
            "Color on ground", dagger_onground_color)
        ui.endmenu()
    ui.separator()

    if ui.beginmenu("Kill Secure"):
        ks_module = ui.checkbox('Enable module', ks_module)
        ui.help("Disabling this module give much worse results")
        ks_restrict_combo = ui.checkbox(
            'Disable module if not orbwalking', ks_restrict_combo)
        ui.separator()
        q_ks = ui.checkbox('Use Q', q_ks)
        ui.separator()
        e_ks = ui.checkbox('Use E', e_ks)
        e_ks_tower = ui.checkbox('Authorize under tower', e_ks_tower)
        ui.separator()
        w_ks = ui.checkbox('Use W', w_ks)
        ui.help("W is used before casting R or to do tricks")
        ui.separator()
        r_ks = ui.checkbox('Use R', r_ks)
        r_ks_value = ui.sliderint("R %", r_ks_value, 1, 100)
        ui.help("Max % of R damage included in ks")
        ui.separator()
        er_ks_tower = ui.checkbox('Authorize ER under tower', er_ks_tower)
        ui.endmenu()
    ui.separator()

    if ui.beginmenu("Combo"):
        combo_module = ui.checkbox('Enable module', combo_module)
        ui.help("May work without this module")
        ui.separator()
        q_combo = ui.checkbox('Use Q', q_combo)
        ui.separator()
        w_combo = ui.checkbox('Use W', w_combo)
        w_combo_close = ui.checkbox('Use close to enemy', w_combo_close)
        ui.help("Without this one W is used only for tricks")
        w_combo_range = ui.sliderint(
            "Distance to enemy", w_combo_range, 200, 500)
        ui.separator()
        e_combo = ui.checkbox('Use E', e_combo)
        e_wait_combo = ui.checkbox('Wait for dagger', e_wait_combo)
        ui.help("If a dagger is on ground it will wait to hit target with it")
        e_combo_tower = ui.checkbox('Authorize under tower', e_combo_tower)
        ui.separator()
        r_combo = ui.checkbox('Use R', r_combo)
        r_combo_value = ui.sliderint("Enemy count to R", r_combo_value, 1, 5)
        ui.endmenu()
    ui.separator()

    if ui.beginmenu("Harass - Not Working"):
        harass_module = ui.checkbox('Enable module', harass_module)
        ui.help("Will automaticly cast thoses spells")
        ui.separator()
        q_harass = ui.checkbox('Use Q', q_harass)
        q_harass_tower = ui.checkbox('Use even under tower', q_harass_tower)
        ui.endmenu()
    ui.separator()

    if ui.beginmenu("Misc"):
        r_width = ui.sliderint("R width", r_width, 300, 550)
        ui.help("R real range is 550")
        r_auto_cancel = ui.checkbox('Auto cancel R', r_auto_cancel)
        ui.help("Cancel R if nobody is in range")
        r_auto_ks = ui.checkbox('Stop R to Kill', r_auto_ks)
        ui.help("Cancel R & use Q / E to kill")
        ui.separator()
        escape_tower = ui.checkbox('Auto escape tower', escape_tower)
        ui.help(
            "Escape of tower if we cannot kill, work as long as u are pressing ModeKite")
        ui.endmenu()
    ui.separator()


def valkyrie_on_load(ctx: Context):
    global r_auto_ks, r_width, e_wait_combo, dagger_draw, dagger_circle, dagger_pts, dagger_thickness, dagger_color, dagger_onground_color, w_combo_close, w_combo_range, escape_tower, r_auto_cancel, e_combo_tower, er_ks_tower, w_ks, e_ks_tower, r_combo_value, r_ks_value, include_clones, harass_module, q_harass, q_harass_tower, ks_module, ks_restrict_combo, q_ks, e_ks, r_ks, combo_module, q_combo, w_combo, e_combo, r_combo

    cfg = ctx.cfg

    include_clones = cfg.get_bool('po_katarina_include_clones', include_clones)

    dagger_draw = cfg.get_bool('po_katarina_dagger_draw', dagger_draw)
    dagger_circle = cfg.get_int('po_katarina_dagger_circle', dagger_circle)
    dagger_pts = cfg.get_int('po_katarina_dagger_pts', dagger_pts)
    dagger_thickness = cfg.get_float(
        'po_katarina_dagger_thickness', dagger_thickness)

    ks_module = cfg.get_bool('po_katarina_ks_module', ks_module)
    ks_restrict_combo = cfg.get_bool(
        'po_katarina_ks_restrict_combo', ks_restrict_combo)
    q_ks = cfg.get_bool('po_katarina_q_ks', q_ks)
    e_ks = cfg.get_bool('po_katarina_e_ks', e_ks)
    e_ks_tower = cfg.get_bool('po_katarina_e_ks_tower', e_ks_tower)
    w_ks = cfg.get_bool('po_katarina_w_ks', w_ks)
    r_ks = cfg.get_bool('po_katarina_r_ks', r_ks)
    r_ks_value = cfg.get_int('po_katarina_r_ks_value', r_ks_value)
    er_ks_tower = cfg.get_bool('po_katarina_er_ks_tower', er_ks_tower)

    combo_module = cfg.get_bool('po_katarina_combo_module', combo_module)
    q_combo = cfg.get_bool('po_katarina_q_combo', q_combo)
    w_combo = cfg.get_bool('po_katarina_w_combo', w_combo)
    w_combo_close = cfg.get_bool('po_katarina_w_combo_close', w_combo_close)
    w_combo_range = cfg.get_int('po_katarina_w_combo_range', w_combo_range)
    e_combo = cfg.get_bool('po_katarina_e_combo', e_combo)
    e_wait_combo = cfg.get_bool('po_katarina_e_wait_combo', e_wait_combo)
    e_combo_tower = cfg.get_bool('po_katarina_e_combo_tower', e_combo_tower)
    r_combo = cfg.get_bool('po_katarina_r_combo', r_combo)
    r_combo_value = cfg.get_int('po_katarina_r_combo_value', r_combo_value)

    # Harass

    r_width = cfg.get_int('po_katarina_r_width', r_width)
    r_auto_cancel = cfg.get_bool('po_katarina_r_auto_cancel', r_auto_cancel)
    escape_tower = cfg.get_bool('po_katarina_escape_tower', escape_tower)
    r_auto_ks = cfg.get_bool('po_katarina_r_auto_ks', r_auto_ks)


def valkyrie_on_save(ctx: Context):
    cfg = ctx.cfg

    cfg.set_bool('po_katarina_include_clones', include_clones)

    cfg.set_bool('po_katarina_dagger_draw', dagger_draw)
    cfg.set_int('po_katarina_dagger_circle', dagger_circle)
    cfg.set_int('po_katarina_dagger_pts', dagger_pts)
    cfg.set_float('po_katarina_dagger_thickness', dagger_thickness)

    cfg.set_bool('po_katarina_ks_module', ks_module)
    cfg.set_bool('po_katarina_ks_restrict_combo', ks_restrict_combo)
    cfg.set_bool('po_katarina_q_ks', q_ks)
    cfg.set_bool('po_katarina_e_ks', e_ks)
    cfg.set_bool('po_katarina_e_ks_tower', e_ks_tower)
    cfg.set_bool('po_katarina_w_ks', w_ks)
    cfg.set_bool('po_katarina_r_ks', r_ks)
    cfg.set_int('po_katarina_r_ks_value', r_ks_value)
    cfg.set_bool('po_katarina_er_ks_tower', er_ks_tower)

    cfg.set_bool('po_katarina_combo_module', combo_module)
    cfg.set_bool('po_katarina_q_combo', q_combo)
    cfg.set_bool('po_katarina_w_combo', w_combo)
    cfg.set_bool('po_katarina_w_combo_close', w_combo_close)
    cfg.set_int('po_katarina_w_combo_range', w_combo_range)
    cfg.set_bool('po_katarina_e_combo', e_combo)
    cfg.set_bool('po_katarina_e_wait_combo', e_wait_combo)
    cfg.set_bool('po_katarina_e_combo_tower', e_combo_tower)
    cfg.set_bool('po_katarina_r_combo', r_combo)
    cfg.set_int('po_katarina_r_combo_value', r_combo_value)

    # Harass

    cfg.set_int('po_katarina_r_width', r_width)
    cfg.set_bool('po_katarina_r_auto_cancel', r_auto_cancel)
    cfg.set_bool('po_katarina_escape_tower', escape_tower)
    cfg.set_bool('po_katarina_r_auto_ks', r_auto_ks)


def get_in_range(player_pos: Vec3, champ_list: list[ChampionObj], range: int):
    count = 0

    for champ in champ_list:
        if player_pos.distance(champ.pos) < range:
            count += 1

    return count


def normalize(start_pos: Vec3, end_pos: Vec3):
    return Vec3(end_pos.x - start_pos.x, end_pos.y - start_pos.y, end_pos.z - start_pos.z).normalize()


def is_new_dagger(missile: list[MissileObj]):
    for dagger in daggers:
        if missile.net_id == dagger.id:
            return False

    return True


def is_dagger_on_ground(dagger: Dagger, missiles: list[MissileObj]):
    for missile in missiles:
        if missile.net_id == dagger.id:
            return False

    return True


def dagger_detection(missiles: list[MissileObj], player_pos: Vec3):
    global daggers

    for missile in missiles:
        is_dagger_arc = missile.name == "katarinaqdaggerarc" or missile.name == "katarinaqdaggerarc2" or missile.name == "katarinaqdaggerarc3" or missile.name == "katarinaqdaggerarc4"

        if missile.name == "katarinawdaggerarc" or is_dagger_arc:
            if is_new_dagger(missile):
                daggers.append(Dagger(missile, player_pos))


def dagger_activator(missiles: list[MissileObj], timestamp: float):
    global daggers

    for dagger in daggers:
        if not dagger.onground and is_dagger_on_ground(dagger, missiles):
            dagger.timestamp = timestamp
            dagger.onground = True


def remove_expired_dagger(timestamp: float):
    global daggers

    daggers_tmp = copy.copy(daggers)

    for dagger in daggers:
        if dagger.onground and dagger.is_expired(timestamp):
            daggers_tmp.remove(dagger)

    daggers = daggers_tmp


def remove_used_dagger(player_pos: Vec3):
    global daggers

    daggers_tmp = copy.copy(daggers)

    for dagger in daggers:
        if dagger.onground and player_pos.distance(dagger.pos) < passive_width:
            daggers_tmp.remove(dagger)

    daggers = daggers_tmp


def draw_handler(ctx: Context):
    if not dagger_draw:
        return

    for dagger in daggers:
        if dagger.onground:
            ctx.circle(ctx.w2s(dagger.pos), dagger_circle, dagger_pts,
                       dagger_thickness, dagger_onground_color)
        else:
            ctx.circle(ctx.w2s(dagger.pos), dagger_circle,
                       dagger_pts, dagger_thickness, dagger_color)


def dagger_handler(ctx: Context, missiles: list[MissileObj]):

    dagger_detection(missiles, ctx.player.pos)
    dagger_activator(missiles, ctx.time)
    remove_expired_dagger(ctx.time)
    remove_used_dagger(ctx.player.pos)


def calculate_passive_dmg(champ: ChampionObj, spell_name: str, spell_static: SpellStatic) -> Damage:
    calculations = Calculations.get(spell_name, None)

    if calculations == None:
        return Damage(0.0)

    extractor = DamageExtractors.get(spell_name, None)

    if extractor == None:
        return Damage(0.0)

    dmg = extractor(calculations, champ, None)

    if spell_static.has_flag(Spell.AppliesOnHit):
        return get_items_onhit_damage(champ, None) + dmg

    return dmg


def cast_q(ctx: Context, target: ChampionObj):
    q_spell = ctx.player.Q

    ctx.cast_spell(q_spell, target.pos)

    return True


def cast_w(ctx: Context):
    w_spell = ctx.player.W

    ctx.cast_spell(w_spell, None)

    return True


def cast_e_unit(ctx: Context, target: ChampionObj):
    e_spell = ctx.player.E

    ctx.cast_spell(e_spell, target.pos)

    return True


def cast_e_dagger(ctx: Context, target_pos: Vec3, dagger_pos: Vec3):
    e_spell = ctx.player.E

    normalized = normalize(dagger_pos, target_pos)

    cast_point = Vec3(dagger_pos.x + passive_width * normalized.x,
                      dagger_pos.y, dagger_pos.z + passive_width * normalized.z)

    ctx.cast_spell(e_spell, cast_point)

    return True


def cast_e_dagger_middle(ctx: Context, dagger_pos: Vec3):
    e_spell = ctx.player.E

    ctx.cast_spell(e_spell, dagger_pos)

    return True


def cast_r(ctx: Context):
    r_spell = ctx.player.R

    Orbwalker.PauseUntil = time() + 0.5
    ctx.cast_spell(r_spell, None)

    return True


def can_e_dagger(target_pos: Vec3, player_pos: Vec3):
    for dagger in daggers:
        if not dagger.onground:
            continue

        if dagger.pos.distance(player_pos) < e_range_dagger and dagger.pos.distance(target_pos) < passive_width + passive_hit_width:
            return dagger.pos

    return None


def is_under_tower(pos: Vec3, turrets: list[TurretObj]):
    for turret in turrets:
        if pos.distance(turret.pos) < tower_range:
            return True

    return False


def ks_handler(ctx: Context, enemies: list[ChampionObj], turrets: list[TurretObj], allies: list[ChampionObj], minions: list[MinionObj], jungle: list[JungleMobObj]):
    player = ctx.player

    passive_static = ctx.get_spell_static("katarinapassive")
    q_spell = player.Q
    w_spell = player.W
    e_spell = player.E
    r_spell = player.R

    passive_dmg = MixedDamage(calculate_passive_dmg(
        player, "katarinapassive", passive_static))
    q_dmg = MixedDamage(calculate_raw_spell_dmg(player, q_spell))
    e_dmg = MixedDamage(calculate_raw_spell_dmg(player, e_spell))
    r_dmg = MixedDamage(calculate_raw_spell_dmg(player, r_spell))

    q_ready = ctx.player.can_cast_spell(q_spell)
    w_ready = ctx.player.can_cast_spell(w_spell)
    e_ready = ctx.player.can_cast_spell(e_spell)
    r_ready = ctx.player.can_cast_spell(r_spell)

    player_under_tower = is_under_tower(player.pos, turrets)

    # Include Flash &  ignite TO_DO

    # Instant R
    if r_ks and r_ready:
        enemies_count = 0
        for enemy in enemies:
            if player.pos.distance(enemy.pos) < r_width:
                enemies_count += 1

        if enemies_count >= 3:
            for enemy in enemies:
                if player.pos.distance(enemy.pos) < r_width:
                    r_real_dmg = r_dmg.calc_against(ctx, ctx.player, enemy)
                    if enemy.health - r_real_dmg * (r_ks_value / 100) <= 0:
                        if w_ks and w_ready:
                            return cast_w(ctx)
                        return cast_r(ctx)

    # E KS
    if e_ks and e_ready:
        for enemy in enemies:
            e_dagger = can_e_dagger(enemy.pos, player.pos)
            passive_real_dmg = passive_dmg.calc_against(ctx, ctx.player, enemy)
            e_real_dmg = e_dmg.calc_against(ctx, ctx.player, enemy)
            enemy_under_tower = is_under_tower(enemy.pos, turrets)

            if (not enemy_under_tower or e_ks_tower) and e_dagger and enemy.health - e_real_dmg - passive_real_dmg <= 0:
                if enemy_under_tower and not player_under_tower and w_ks and w_ready:
                    return cast_w(ctx)
                return cast_e_dagger(ctx, enemy.pos, e_dagger)

            if player.pos.distance(enemy.pos) < e_range_enemy and enemy.health - e_real_dmg <= 0:
                if enemy_under_tower and not player_under_tower and w_ks and w_ready:
                    return cast_w(ctx)
                return cast_e_unit(ctx, enemy)

    # Q KS
    if q_ks and q_ready:
        for enemy in enemies:
            q_real_dmg = q_dmg.calc_against(ctx, ctx.player, enemy)

            if player.pos.distance(enemy.pos) < q_range and enemy.health - q_real_dmg <= 0:
                return cast_q(ctx, enemy)

    # QE KS
    if q_ks and e_ks and q_ready and e_ready:
        for enemy in enemies:
            passive_real_dmg = passive_dmg.calc_against(ctx, ctx.player, enemy)
            q_real_dmg = q_dmg.calc_against(ctx, ctx.player, enemy)
            e_real_dmg = e_dmg.calc_against(ctx, ctx.player, enemy)
            e_dagger = can_e_dagger(enemy.pos, player.pos)
            enemy_under_tower = is_under_tower(enemy.pos, turrets)

            if (not enemy_under_tower or e_ks_tower) and e_dagger and enemy.health - q_real_dmg - e_real_dmg - passive_real_dmg <= 0:
                if player.pos.distance(enemy.pos) < q_range:
                    return cast_q(ctx, enemy)
                else:
                    if enemy_under_tower and not player_under_tower and w_ks and w_ready:
                        return cast_w(ctx)
                    else:
                        return cast_e_dagger(ctx, enemy.pos, e_dagger)

            if (not enemy_under_tower or e_ks_tower) and player.pos.distance(enemy.pos) < e_range_enemy and enemy.health - q_real_dmg - e_real_dmg <= 0:
                if player.pos.distance(enemy.pos) < q_range:
                    return cast_q(ctx, enemy)
                if enemy_under_tower and not player_under_tower and w_ks and w_ready:
                    return cast_w(ctx)
                else:
                    return cast_e_unit(ctx, enemy)

    # E to Q KS
    if q_ks and e_ks and q_ready and e_ready:
        for enemy in enemies:
            q_real_dmg = q_dmg.calc_against(ctx, ctx.player, enemy)

            for dagger in daggers:
                if enemy.health - q_real_dmg <= 0 and player.pos.distance(dagger.pos) < e_range_dagger and enemy.pos.distance(dagger.pos) < q_range:
                    return cast_e_dagger(ctx, enemy.pos, dagger.pos)

            if enemy.health - q_real_dmg > 0:
                continue

            for enemy2 in enemies:
                if player.pos.distance(enemy2.pos) < e_range_enemy and enemy.pos.distance(enemy2.pos) < q_range:
                    return cast_e_unit(ctx, enemy2)

            for ally in allies:
                if player.pos.distance(ally.pos) < e_range_enemy and enemy.pos.distance(ally.pos) < q_range:
                    return cast_e_unit(ctx, ally)

            for minion in minions:
                if player.pos.distance(minion.pos) < e_range_enemy and enemy.pos.distance(minion.pos) < q_range:
                    return cast_e_unit(ctx, minion)

            for jgl in jungle:
                if player.pos.distance(jgl.pos) < e_range_enemy and enemy.pos.distance(jgl.pos) < q_range:
                    return cast_e_unit(ctx, jgl)

    # QER KS
    if q_ks and e_ks and r_ks and q_ready and e_ready and r_ready:
        for enemy in enemies:
            passive_real_dmg = passive_dmg.calc_against(
                ctx, ctx.player, enemy)
            q_real_dmg = q_dmg.calc_against(ctx, ctx.player, enemy)
            e_real_dmg = e_dmg.calc_against(ctx, ctx.player, enemy)
            r_real_dmg = r_dmg.calc_against(ctx, ctx.player, enemy)
            e_dagger = can_e_dagger(enemy.pos, player.pos)
            enemy_under_tower = is_under_tower(enemy.pos, turrets)

            if (not enemy_under_tower or er_ks_tower) and e_dagger and enemy.health - q_real_dmg - e_real_dmg - passive_real_dmg - r_real_dmg * (r_ks_value / 100) <= 0:
                if player.pos.distance(enemy.pos) < q_range:
                    return cast_q(ctx, enemy)
                else:
                    if enemy_under_tower and not player_under_tower and w_ks and w_ready:
                        return cast_w(ctx)
                    return cast_e_dagger(ctx, enemy.pos, e_dagger)

            if (not enemy_under_tower or er_ks_tower) and player.pos.distance(enemy.pos) < e_range_enemy and enemy.health - q_real_dmg - e_real_dmg - r_real_dmg * (r_ks_value / 100) <= 0:
                if player.pos.distance(enemy.pos) < q_range:
                    return cast_q(ctx, enemy)
                if enemy_under_tower and not player_under_tower and w_ks and w_ready:
                    return cast_w(ctx)
                return cast_e_unit(ctx, enemy)

    # ER KS
    if e_ks and r_ks and e_ready and r_ready:
        for enemy in enemies:
            passive_real_dmg = passive_dmg.calc_against(ctx, ctx.player, enemy)
            e_real_dmg = e_dmg.calc_against(ctx, ctx.player, enemy)
            r_real_dmg = r_dmg.calc_against(ctx, ctx.player, enemy)
            e_dagger = can_e_dagger(enemy.pos, player.pos)
            enemy_under_tower = is_under_tower(enemy.pos, turrets)

            if (not enemy_under_tower or er_ks_tower) and e_dagger and enemy.health - e_real_dmg - passive_real_dmg - r_real_dmg * (r_ks_value / 100) <= 0:
                if enemy_under_tower and not player_under_tower and w_ks and w_ready:
                    return cast_w(ctx)
                return cast_e_dagger(ctx, enemy.pos, e_dagger)

            if (not enemy_under_tower or er_ks_tower) and player.pos.distance(enemy.pos) < e_range_enemy and enemy.health - e_real_dmg - r_real_dmg * (r_ks_value / 100) <= 0 and player.pos.distance(enemy.pos) < e_range_enemy:
                if enemy_under_tower and not player_under_tower and w_ks and w_ready:
                    return cast_w(ctx)
                return cast_e_unit(ctx, enemy)

    # QR KS
    if q_ks and r_ks and q_ready and r_ready:
        for enemy in enemies:
            if player.pos.distance(enemy.pos) < r_width:
                q_real_dmg = q_dmg.calc_against(ctx, ctx.player, enemy)
                r_real_dmg = r_dmg.calc_against(ctx, ctx.player, enemy)

                if enemy.health - q_real_dmg - r_real_dmg * (r_ks_value / 100) <= 0:
                    return cast_q(ctx, enemy)

    # E to QR KS
    # E to R KS

    # R KS
    if r_ks and r_ready:
        for enemy in enemies:
            if player.pos.distance(enemy.pos) < r_width:
                r_real_dmg = r_dmg.calc_against(ctx, ctx.player, enemy)
                if enemy.health - r_real_dmg * (r_ks_value / 100) <= 0:
                    if w_ks and w_ready:
                        return cast_w(ctx)
                    return cast_r(ctx)

    return False


def escape_handler(ctx: Context, enemies: list[ChampionObj], turrets: list[TurretObj], allies: list[ChampionObj], minions: list[MinionObj], jungle: list[JungleMobObj]):
    player = ctx.player
    e_spell = player.E
    e_ready = ctx.player.can_cast_spell(e_spell)
    player_under_tower = is_under_tower(player.pos, turrets)

    if not player_under_tower:
        return False

    if e_ready:
        for dagger in daggers:
            if player.pos.distance(dagger.pos) < e_range_dagger and not is_under_tower(dagger.pos, turrets):
                return cast_e_dagger_middle(ctx, dagger.pos)

        for enemy in enemies:
            if player.pos.distance(enemy.pos) < e_range_enemy and not is_under_tower(enemy.pos, turrets):
                return cast_e_unit(ctx, enemy)

        for ally in allies:
            if player.pos.distance(ally.pos) < e_range_enemy and not is_under_tower(ally.pos, turrets):
                return cast_e_unit(ctx, ally)

        for minion in minions:
            if player.pos.distance(minion.pos) < e_range_enemy and not is_under_tower(minion.pos, turrets):
                return cast_e_unit(ctx, minion)

        for jgl in jungle:
            if player.pos.distance(jgl.pos) < e_range_enemy and not is_under_tower(jgl.pos, turrets):
                return cast_e_unit(ctx, jgl)


def should_e(target_pos: Vec3, distance_to_target: float):
    if not e_wait_combo:
        return True

    if q_throw:
        return False

    if len(daggers) == 0:
        return True

    for dagger in daggers:
        if distance_to_target > dagger.pos.distance(target_pos):
            return False

    return True


def combo_handler(ctx: Context, target: ChampionObj, enemies: list[ChampionObj], turrets: list[TurretObj]):
    player = ctx.player

    q_spell = player.Q
    w_spell = player.W
    e_spell = player.E
    r_spell = player.R

    w_ready = ctx.player.can_cast_spell(w_spell)

    distance_to_target = player.pos.distance(target.pos)
    player_under_tower = is_under_tower(player.pos, turrets)
    target_under_tower = is_under_tower(target.pos, turrets)
    e_combo_tower

    if q_combo and ctx.player.can_cast_spell(q_spell) and distance_to_target < q_range:
        return cast_q(ctx, target)

    if e_combo and ctx.player.can_cast_spell(e_spell):
        e_dagger = can_e_dagger(target.pos, player.pos)

        if e_dagger:
            if not target_under_tower or e_combo_tower:
                if target_under_tower and not player_under_tower and w_ready:
                    return cast_w(ctx)
                return cast_e_dagger(ctx, target.pos, e_dagger)
        else:
            if should_e(target.pos, distance_to_target):
                if distance_to_target < e_range_enemy:
                    if target_under_tower and not player_under_tower and w_ready:
                        return cast_w(ctx)
                    return cast_e_unit(ctx, target)

    if w_combo and w_ready and w_combo_close and distance_to_target < w_combo_range:
        return cast_w(ctx)

    if r_combo and ctx.player.can_cast_spell(r_spell) and get_in_range(player.pos, enemies, r_width) >= r_combo_value:
        if w_combo and w_ready:
            return cast_w(ctx)
        return cast_r(ctx)

    return False


def can_move(player: ChampionObj, enemies: list[ChampionObj]):
    is_under_r = player.has_buff("katarinarsound")

    if not is_under_r:
        Orbwalker.PauseUntil = 0.0
        return True

    if not r_auto_cancel:
        Orbwalker.PauseUntil = time() + 0.5
        return False

    if get_in_range(player.pos, enemies, 550) == 0:
        Orbwalker.PauseUntil = 0.0
        return True

    Orbwalker.PauseUntil = time() + 0.5
    return False


def q_being_trow(missiles: list[MissileObj]):
    global q_throw

    if not e_wait_combo:
        q_throw = False
        return

    for missile in missiles:
        if missile.name == 'katarinaq':
            q_throw = True
            break


def valkyrie_exec(ctx: Context):
    player = ctx.player
    missiles = ctx.missiles.ally_to(player).get()

    dagger_handler(ctx, missiles)

    if player.dead or player.recalling:
        return

    q_being_trow(missiles)

    draw_handler(ctx)

    if include_clones:
        enemies = ctx.champs.enemy_to(
            player).targetable().near(player, fight_range).get()
    else:
        enemies = ctx.champs.enemy_to(
            player).targetable().near(player, fight_range).not_clone().get()

    turrets = ctx.turrets.enemy_to(
        player).alive().near(player.pos, fight_range).get()
    allies = ctx.champs.ally_to(player).alive(
    ).targetable().near(player, e_range_enemy).get()
    minions = ctx.minions.alive().targetable().near(player, e_range_enemy).get()
    jungle = ctx.jungle.alive().targetable().near(player, e_range_enemy).get()

    is_combo = Orbwalker.CurrentMode == Orbwalker.ModeKite

    if not can_move(player, enemies):
        if r_auto_ks and ks_module and (not ks_restrict_combo or is_combo):
            ks_handler(ctx, enemies, turrets, allies, minions, jungle)
        return

    if is_combo and escape_tower:
        if escape_handler(ctx, enemies, turrets, allies, minions, jungle):
            return

    if len(enemies) == 0:
        return

    if ks_module and (not ks_restrict_combo or is_combo):
        if ks_handler(ctx, enemies, turrets, allies, minions, jungle):
            return

    target = target_selector.get_target(ctx, enemies)

    if is_combo and combo_module:
        combo_handler(ctx, target, enemies, turrets)
